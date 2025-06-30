import frappe
from frappe.model.document import Document

class CutiTahunan(Document):
    def after_insert(self):
        try:
            # Ambil divisi dari karyawan pemohon
            divisi_pemohon = frappe.get_value(
                "Karyawan",
                filters={"name": self.karyawan_pemohon},
                fieldname="divisi"
            )

            # Urutan approval
            steps = [
                {"urutan": 2, "jabatan": "Manager", "divisi": divisi_pemohon},
                {"urutan": 3, "jabatan": "General Manager"},
                {"urutan": 4, "jabatan": "Direktur Operasional"},
            ]

            self.append("approval", {
                "urutan": 1,
                "karyawan": self.karyawan_penerima_job_pending,
                "status_ttd": "Menunggu",
                "waktu_status_dirubah": frappe.utils.now()
            })

            for step in steps:
                user = get_karyawan_by_jabatan(step["jabatan"], step.get("divisi"))

                self.append("approval", {
                    "urutan": step["urutan"],
                    "jabatan": step["jabatan"],
                    "divisi": step.get("divisi"),
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
        all_approved = all([appr.status_tanda_tangan == "Disetujui" for appr in self.approval])
        if all_approved and not self.doc_url:
            try:
                print("bangk")
                # file_url = buat_file_docx(self)
                # # Misal, kamu punya field file_docx di doctype buat nyimpen file url
                # self.file_docx = file_url
                # self.save(ignore_permissions=True)
            except Exception as e:
                frappe.log_error(frappe.get_traceback(), f"[CutiTahunan: {self.name}] Gagal generate file DOCX: {str(e)}")

# Fungsi helper di luar class
def get_karyawan_by_jabatan(jabatan, divisi=None):
    filters = {"jabatan": jabatan}
    if divisi:
        filters["divisi"] = divisi

    # Ambil user_id dari Karyawan berdasarkan jabatan dan (jika ada) divisi
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
            frappe.log_error(f"Failed to send notification steps for CutiTahunan", message=str(e))
