import frappe
from frappe.model.document import Document
from oims.utils.document_generator import (
    generate_docx_from_template,
    save_base64_signature_to_file,
    upload_to_file_manager,
    formatdate_indonesia,
    formatdate_indonesia_with_day,
    build_inline_image,
)
from docxtpl import DocxTemplate

class PengajuanCuti(Document):
    def before_insert(self):
        posisi_site = frappe.get_value(
            "Karyawan",
            filters={"name": self.karyawan_pemohon},
            fieldname="posisi_site"
        )
        if posisi_site == "HO":
            self.jenis_cuti = "Cuti Tahunan (HO)"
    def after_insert(self):
        try:
            # Ambil divisi dari karyawan pemohon
            divisi_pemohon = frappe.get_value(
                "Karyawan",
                filters={"name": self.karyawan_pemohon},
                fieldname="divisi"
            )

            if self.jenis_cuti == "Cuti Tahunan (HO)":
                steps = [
                    {"urutan": 2, "jabatan": "Manager", "divisi": divisi_pemohon},
                    {"urutan": 3, "jabatan": "General Manager"},
                    {"urutan": 4, "jabatan": "Direktur Operasional"},
                ]
            elif self.jenis_cuti == "Cuti Pulang Staff Lapangan":
                # Ambil dari field projek jika ada, agar approval bisa by project/site
                projek = getattr(self, "projek", None)
                steps = [
                    {"urutan": 2, "jabatan": "Site Manager", "projek": projek},
                    {"urutan": 3, "jabatan": "Project Manager", "projek": projek},
                    {"urutan": 4, "jabatan": "Direktur Operasional"},
                ]
            else:
                steps = []

            self.append("approval", {
                "urutan": 1,
                "karyawan": self.karyawan_penerima_job_pending,
                "status_ttd": "Menunggu",
                "waktu_status_dirubah": frappe.utils.now()
            })

            for step in steps:
                # Untuk approval lapangan, cari user by projek jika ada
                user = None
                if "projek" in step and step["projek"]:
                    user = get_karyawan_by_jabatan_and_projek(step["jabatan"], step["projek"])
                else:
                    user = get_karyawan_by_jabatan(step["jabatan"], step.get("divisi"))
                self.append("approval", {
                    "urutan": step["urutan"],
                    "jabatan": step.get("jabatan"),
                    "divisi": step.get("divisi"),
                    "projek": step.get("projek"),
                    "karyawan": user,
                    "status_ttd": "Menunggu",
                    "waktu_status_dirubah": frappe.utils.now()
                })


            self.save()

            nama_pemohon = frappe.get_value(
                "Karyawan",
                filters={"name": self.karyawan_pemohon},
                fieldname="nama_lengkap"
            )
            employee_id_penerima = self.karyawan_penerima_job_pending
            data_penerima = frappe.get_value(
                "Karyawan",
                filters={"name": employee_id_penerima},
                fieldname=["nama_lengkap", "user_id"],
                as_dict=True
            )
            keperluan = self.keperluan
            tanggal_mulai_cuti = self.tanggal_mulai_cuti
            tanggal_selesai_cuti = self.tanggal_selesai_cuti
            selama_hari = self.selama_hari

            # --- Panggil notifikasi
            send_notification(
                self.name,
                nama_pemohon,
                data_penerima.user_id,
                data_penerima.nama_lengkap,
                keperluan,
                tanggal_mulai_cuti,
                tanggal_selesai_cuti,
                selama_hari
            )

        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"[Cuti Tahunan: {self.name}] Failed to create approval steps: {str(e)}")

    def on_update(self):
        try:
            all_approved = all([appr.status_tanda_tangan == "Disetujui" for appr in self.approval])
            if all_approved and not self.doc_url:
                if not self.no_surat:
                    now = frappe.utils.now_datetime()
                    no_surat = f"CT-{now.strftime('%H%M%S')}"
                    self.no_surat = no_surat

                doc_file = generate_cuti_document(self)
                if doc_file:
                    file_name = f"Cuti_{self.no_surat.replace('/', '_')}.docx"
                    file_url = upload_to_file_manager(doc_file, file_name, 'Cuti Tahunan')
                    self.doc_url = file_url
                    self.save(ignore_permissions=True)

                    # === Kirim notifikasi ke karyawan pemohon ===
                    # Ambil data karyawan pemohon (user_id)
                    karyawan_pemohon = frappe.get_doc("Karyawan", self.karyawan_pemohon)
                    print('karyawan')
                    print(karyawan_pemohon)
                    if karyawan_pemohon and getattr(karyawan_pemohon, "user_id", None):
                        description = f"""
                            Pengajuan cuti tahunan Anda sudah disetujui semua.
                            Surat cuti sudah berhasil dibuat dan bisa anda download di halaman deail pengajuan cuti.
                            Klik tombol dibawah untuk melihat halaman detail pengajuan cuti dan download surat.
                        """
                        frappe.get_doc({
                            "doctype": "OIMS Notification",
                            "title": "Surat Cuti Tahunan Siap Diunduh",
                            "description": description.strip(),
                            "user": karyawan_pemohon.user_id,
                            "type": "Cuti",
                            "link_to": f"/pengajuan-cuti/{self.name}",
                            "link_to_label": "Lihat Pengajuan"
                        }).insert(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(frappe.get_traceback(), f"[PengajuanCuti: {self.name}] Gagal generate file DOCX: {str(e)}")


# Fungsi helper di luar class
def get_karyawan_by_jabatan(jabatan, divisi=None):
    filters = {"jabatan": jabatan}
    if divisi:
        filters["divisi"] = divisi

    # Ambil user_id dari Karyawan berdasarkan jabatan dan (jika ada) divisi
    karyawan = frappe.get_value("Karyawan", filters=filters, fieldname="name")
    return karyawan or None

def get_karyawan_by_jabatan_and_projek(jabatan, projek):
    filters = {"jabatan": jabatan}
    if projek:
        filters["projek"] = projek
    karyawan = frappe.get_value("Karyawan", filters=filters, fieldname="name")
    return karyawan or None

def send_notification(name, nama_pemohon, user_id_penerima, nama_penerima, keperluan, tanggal_mulai_cuti, tanggal_selesai_cuti, selama_hari):
    description_hr = f"""
        [{name}] {nama_pemohon} mengajukan cuti tahunan:

        🗓️ Tanggal Cuti: {tanggal_mulai_cuti} s.d. {tanggal_selesai_cuti}
        📅 Selama: {selama_hari} hari
        🎯 Keperluan: {keperluan}
        🔁 Penerima tugas selama cuti: {nama_penerima or '-'}
        """

    description_penerima = f"""
        [{name}] Anda ditunjuk oleh {nama_pemohon} untuk menerima tugas selama masa cuti:

        🗓️ {tanggal_mulai_cuti} s.d. {tanggal_selesai_cuti}
        📅 Total: {selama_hari} hari
        🎯 Keperluan: {keperluan}
        📄 Harap tandatangani formulir cuti tahunan tersebut.
        """

    try:
        jabatan_hr = frappe.get_value(
                "Jabatan",
                filters={"name": "HR"},
                fieldname="name"
            )

        if not jabatan_hr:
            frappe.log_error("Tidak ditemukan Jabatan 'HR' pada proses pembuatan cuti tahunan")
            return

        frappe.get_doc({
            "doctype": "OIMS Notification",
            "title": "Pengajuan Cuti Tahunan Baru",
            "description": description_hr.strip(),
            "jabatan": jabatan_hr,
            "type": "Cuti",
            "link_to": f"/pengajuan-cuti/{name}",
            "link_to_label": "Lihat Pengajuan Cuti"
        }).insert(ignore_permissions=True)

        frappe.get_doc({
            "doctype": "OIMS Notification",
            "title": "Tanda Tangan Pengalihan Tugas Cuti",
            "description": description_penerima.strip(),
            "user": user_id_penerima,
            "type": "Cuti",
            "link_to": f"/pengajuan-cuti/{name}",
            "link_to_label": "Tandatangani Formulir"
        }).insert(ignore_permissions=True)
    except Exception as e:
            frappe.log_error(f"Failed to send notification steps for PengajuanCuti", message=str(e))

def generate_cuti_document(self):
    # Ambil docx template lebih awal
    template_path = frappe.get_app_path('oims', 'templates', 'docs', 'form_cuti.docx')
    output_name = f"Cuti_{self.no_surat}.docx"
    doc = DocxTemplate(template_path)

    # Siapkan variable default kosong
    ttd_pemohon_img = ''
    ttd_penerima_img = ''
    ttd_manager_img = ''
    ttd_gm_img = ''
    ttd_do_img = ''

    # Pemohon
    karyawan_pemohon = frappe.get_doc("Karyawan", self.karyawan_pemohon)
    if getattr(karyawan_pemohon, "ttd", ""):
        ttd_pemohon_img = build_inline_image(doc, save_base64_signature_to_file(karyawan_pemohon.ttd, prefix="ttd_pemohon"), width=60, height=40)

    # Approval loop berdasarkan urutan
    approval_list = sorted(self.approval, key=lambda appr: appr.urutan)
    karyawan_penerima = None

    for i, appr in enumerate(approval_list):
        if not appr.karyawan:
            continue
        karyawan = frappe.get_doc("Karyawan", appr.karyawan)
        ttd_img = build_inline_image(doc, save_base64_signature_to_file(getattr(karyawan, "ttd", ""), prefix=f"ttd_urutan_{appr.urutan}"), width=60, height=40) if getattr(karyawan, "ttd", "") else ''

        if appr.urutan == 1:
            karyawan_penerima = karyawan
            ttd_penerima_img = ttd_img
        elif appr.urutan == 2:
            ttd_manager_img = ttd_img
        elif appr.urutan == 3:
            ttd_gm_img = ttd_img
        elif appr.urutan == 4:
            ttd_do_img = ttd_img

    context = {
        'tanggal_surat_dibuat': formatdate_indonesia(frappe.utils.nowdate()),
        'nama_pemohon': karyawan_pemohon.nama_lengkap,
        'jabatan_pemohon': karyawan_pemohon.jabatan,
        'nrp_pemohon': karyawan_pemohon.nrp,
        'selama_hari': self.selama_hari,
        'tanggal_mulai_cuti': formatdate_indonesia(self.tanggal_mulai_cuti),
        'tanggal_selesai_cuti': formatdate_indonesia(self.tanggal_selesai_cuti),
        'keperluan': self.keperluan,
        'nama_penerima': getattr(karyawan_penerima, "nama_lengkap", ""),
        'jabatan_penerima': getattr(karyawan_penerima, "jabatan", ""),
        'nrp_penerima': getattr(karyawan_penerima, "nrp", ""),
        'no_surat': self.no_surat,
        'ttd_pemohon': ttd_pemohon_img,
        'ttd_penerima': ttd_penerima_img,
        'ttd_manager': ttd_manager_img,
        'ttd_gm': ttd_gm_img,
        'ttd_do': ttd_do_img,
    }

    doc.render(context)
    output_path = frappe.utils.get_site_path('private', 'files', output_name)
    doc.save(output_path)
    return output_path
