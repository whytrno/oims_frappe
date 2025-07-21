import frappe
from frappe.utils import getdate
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist(methods=["GET"])
def get_all_self_cuti() -> list[dict]:
    try:
        user_id = frappe.session.user

        karyawan = frappe.db.get_value(
            'Karyawan',
            {'user_id': user_id},
            'name',
            as_dict=True
        )

        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        data = frappe.get_all(
            "Pengajuan Cuti",
            fields=["name", "karyawan_pemohon", "keperluan", "karyawan_penerima_job_pending", "tanggal_mulai_cuti", "tanggal_selesai_cuti", "selama_hari", "jenis_cuti", "projek", "rute_cuti", "tanggal_tiket_cuti", "tanggal_tiket_on_site"],
            filters={
                "karyawan_pemohon": karyawan.name,
            },
            limit=999999,
        )

        for cuti in data:
            nama_karyawan_pemohon = frappe.get_value("Karyawan", cuti["karyawan_pemohon"], "nama_lengkap")
            nama_karyawan_penerima_job_pending = frappe.get_value("Karyawan", cuti["karyawan_penerima_job_pending"], "nama_lengkap")

            cuti["nama_karyawan_pemohon"] = nama_karyawan_pemohon
            cuti["nama_karyawan_penerima_job_pending"] = nama_karyawan_penerima_job_pending

            approval_rows = frappe.get_all(
                "Pengajuan Cuti Approval",
                filters={"parent": cuti["name"], "parenttype": "Pengajuan Cuti"},
                fields=["status_tanda_tangan"]
            )

            ada_ditolak = any(
                (row.status_tanda_tangan or "").lower() == "ditolak"
                for row in approval_rows
            )

            if ada_ditolak:
                cuti["status"] = "Ditolak"
            elif approval_rows and all(
                (row.status_tanda_tangan or "").lower() != "menunggu"
                for row in approval_rows
            ):
                cuti["status"] = "Disetujui"
            else:
                cuti["status"] = "Proses"

        return response_success("Berhasil mengambil data lokasi pengajuan cuti.", data=data)
    except Exception as e:
        return response_error("Terjadi kesalahan saat mengambil data pengajuan cuti.", http_status_code=500)

@frappe.whitelist(methods=["POST"])
def create_cuti_tahunan(karyawan_penerima_job_pending, tanggal_mulai_cuti, tanggal_selesai_cuti, keperluan=None, rute_cuti=None, tanggal_tiket_cuti=None, tanggal_tiket_on_site=None):
    try:
        user_id = frappe.session.user

        karyawan = frappe.db.get_value(
            'Karyawan',
            {'user_id': user_id},
            ['name', 'posisi_site'],
            as_dict=True
        )
        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        karyawan_penerima_name = frappe.db.get_value(
            'Karyawan', karyawan_penerima_job_pending, 'name'
        )
        if not karyawan_penerima_name:
            return response_error("Data karyawan penerima job pending tidak ditemukan.", http_status_code=404)

        try:
            tanggal_mulai = getdate(tanggal_mulai_cuti)
            tanggal_selesai = getdate(tanggal_selesai_cuti)
            tanggal_tiket_cuti = getdate(tanggal_tiket_cuti) if tanggal_tiket_cuti else None
            tanggal_tiket_on_site = getdate(tanggal_tiket_on_site) if tanggal_tiket_on_site else None
            selama_hari = (tanggal_selesai - tanggal_mulai).days + 1
        except Exception as e:
            return response_error("Format tanggal tidak valid.", http_status_code=400)

        doc = frappe.get_doc({
            "doctype": "Pengajuan Cuti",
            "karyawan_pemohon": karyawan.name,
            "projek": karyawan.posisi_site,
            "rute_cuti": rute_cuti,
            "karyawan_penerima_job_pending": karyawan_penerima_name,
            "tanggal_mulai_cuti": tanggal_mulai,
            "tanggal_selesai_cuti": tanggal_selesai,
            "selama_hari": selama_hari,
            "keperluan": keperluan,
            "tanggal_tiket_cuti": tanggal_tiket_cuti,
            "tanggal_tiket_on_site": tanggal_tiket_on_site,
        })
        doc.insert()
        frappe.db.commit()

        return response_success("Pengajuan cuti berhasil dibuat.", data={"cuti_id": doc.name})

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error create_cuti_tahunan")
        return response_error(
            "Terjadi kesalahan saat membuat data pengajuan cuti.",
            http_status_code=500,
        )

@frappe.whitelist(methods=["GET"])
def get_cuti_tahunan_detail(name) -> dict:
    try:
        user_id = frappe.session.user

        karyawan = frappe.db.get_value(
            'Karyawan',
            {'user_id': user_id},
            'name',
            as_dict=True
        )

        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        cuti = frappe.get_value(
            "Pengajuan Cuti",
            name,
            ["no_surat", "doc_url", "name", "karyawan_pemohon", "keperluan", "karyawan_penerima_job_pending", "tanggal_mulai_cuti", "tanggal_selesai_cuti", "selama_hari", "jenis_cuti", "projek", "rute_cuti", "tanggal_tiket_cuti", "tanggal_tiket_on_site", "creation"],
            as_dict=True
        )

        if not cuti:
            return response_error("Data pengajuan cuti tidak ditemukan.", http_status_code=404)

        # Enrich data
        cuti["nama_karyawan_pemohon"] = frappe.get_value("Karyawan", cuti["karyawan_pemohon"], "nama_lengkap")
        cuti["nama_karyawan_penerima_job_pending"] = frappe.get_value("Karyawan", cuti["karyawan_penerima_job_pending"], "nama_lengkap")

        # --- Timeline Logic ---
        timeline = []
        # 1. Selalu ada pengajuan pengajuan cuti
        timeline.append({
            "title": "Pengajuan pengajuan cuti",
            "datetime": str(cuti.get("creation"))
        })

        # 2. Cek child table approval
        approval_rows = frappe.get_all(
            "Pengajuan Cuti Approval",
            filters={"parent": cuti["name"], "parenttype": "Pengajuan Cuti"},
            fields=["urutan", "karyawan", "jabatan", "status_tanda_tangan", "waktu_status_dirubah"],
            order_by="urutan desc"
        )

        ada_ditolak = any(
            (row.status_tanda_tangan or "").lower() == "ditolak"
            for row in approval_rows
        )

        if ada_ditolak:
            cuti["status"] = "Ditolak"
        elif approval_rows and all(
            (row.status_tanda_tangan or "").lower() != "menunggu"
            for row in approval_rows
        ):
            cuti["status"] = "Disetujui"
        else:
            cuti["status"] = "Proses"

        for app in approval_rows:
            if app.status_tanda_tangan and app.status_tanda_tangan.lower() != "menunggu" and app.waktu_status_dirubah:
                approval_nama_lengkap = frappe.get_value(
                    "Karyawan", app.karyawan, "nama_lengkap"
                )

                if app.status_tanda_tangan.lower() == "disetujui":
                    action = "menandatangani"
                elif app.status_tanda_tangan.lower() == "ditolak":
                    action = "menolak"
                else:
                    action = ""

                if app.urutan == 1:
                    title = f"{approval_nama_lengkap} (Penerima job pending) telah {action}"
                else:
                    title = f"{approval_nama_lengkap} ({app.jabatan}) {action}"

                timeline.append({
                    "title": title,
                    "status": app.status_tanda_tangan.lower(),
                    "datetime": str(app.waktu_status_dirubah)
                })
        # sort timeline desc, terbaru di atas (opsional)
        timeline = sorted(timeline, key=lambda x: x["datetime"], reverse=True)
        cuti["timeline"] = timeline

        return response_success("Berhasil mengambil detail pengajuan cuti.", data=cuti)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error get_cuti_tahunan_detail: {str(e)}")
        return response_error("Terjadi kesalahan saat mengambil data pengajuan cuti.", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def get_approval_rights(name):
    """Cek apakah user login sudah saatnya tanda tangan atau sudah menandatangani."""

    try:
        user_id = frappe.session.user

        # Cari employee id dari user login
        karyawan_name = str(frappe.db.get_value(
            "Karyawan",
            {"user_id": user_id},
            "name"
        ))

        if not karyawan_name:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        # Ambil approval rows untuk pengajuan cuti ini
        approval_rows = frappe.get_all(
            "Pengajuan Cuti Approval",
            filters={"parent": name, "parenttype": "Pengajuan Cuti"},
            fields=["urutan", "karyawan", "status_tanda_tangan", "waktu_status_dirubah"],
            order_by="urutan asc"
        )

        # Flag output
        is_next_approver = False
        already_signed = False
        your_approval = None

        # Loop approval rows cari punya user
        for idx, row in enumerate(approval_rows):
            if row.karyawan == karyawan_name:
                your_approval = row
                if row.status_tanda_tangan and row.status_tanda_tangan.lower() == "menunggu":
                    # Apakah ini adalah approval "pertama yang menunggu"? (yaitu urutan approval yang sekarang)
                    # Cek semua approval sebelum ini harus sudah signed (bukan "Menunggu")
                    if idx == 0 or all(r.status_tanda_tangan.lower() != "menunggu" for r in approval_rows[:idx]):
                        is_next_approver = True
                    # else: approval sebelumnya belum signed
                elif row.status_tanda_tangan and row.status_tanda_tangan.lower() != "menunggu":
                    already_signed = True
                break

        result = {
            "is_next_approver": is_next_approver,
            "already_signed": already_signed,
            "your_approval": your_approval
        }

        return response_success("Status approval berhasil diambil.", data=result)
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error get_approval_rights: {str(e)}")
        return response_error("Terjadi kesalahan saat mengambil status approval.", http_status_code=500)

@frappe.whitelist(allow_guest=False, methods=["POST"])
def sign_cuti_tahunan_approval(name, action=None):
    """
    User login menandatangani approval pada dokumen Pengajuan Cuti (child table).
    Juga otomatis kirim notifikasi ke approval urutan berikutnya (jika ada).
    """
    try:
        user_id = frappe.session.user

        employee_data = frappe.db.get_value(
            "Karyawan",
            {"user_id": user_id},
            ["name", "user_id", "nama_lengkap"],
            as_dict=True
           )
        if not employee_data:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)
        karyawan_name = str(employee_data.name)

        if action not in ("approve", "reject"):
            return response_error("Parameter action harus 'approve' atau 'reject'.", http_status_code=400)

        doc = frappe.get_doc("Pengajuan Cuti", name)
        approval_found = False
        next_approval = None

        status_value = "Disetujui" if action == "approve" else "Ditolak"

        # Cari baris approval yang akan di-sign & cari urutan berikutnya
        approval_rows = list(doc.approval)
        for idx, row in enumerate(approval_rows):
            if row.karyawan == karyawan_name and (row.status_tanda_tangan or "").lower() == "menunggu":
                row.status_tanda_tangan = status_value
                row.waktu_status_dirubah = frappe.utils.now()
                approval_found = True
                # cari next
                if idx + 1 < len(approval_rows):
                    next_row = approval_rows[idx + 1]
                    if next_row.status_tanda_tangan.lower() == "menunggu" and next_row.karyawan:
                        next_approval = next_row
                break

        if not approval_found:
            return response_error("Tidak ditemukan approval yang perlu Anda tandatangani.", http_status_code=403)

        doc.save()
        frappe.db.commit()

        # Jika ada approval urutan berikutnya, kirim notifikasi
        if next_approval:
            if action == "approve":
                # Dapatkan data karyawan & user_id untuk notifikasi
                user_id_penerima = frappe.get_value("Karyawan", next_approval.karyawan, "user_id")
                nama_pemohon = employee_data.nama_lengkap
                tanggal_mulai_cuti = doc.tanggal_mulai_cuti
                tanggal_selesai_cuti = doc.tanggal_selesai_cuti
                selama_hari = doc.selama_hari
                keperluan = doc.keperluan

                description_penerima = f"""
                    [{name}] Pengajuan Surat Cuti baru oleh {nama_pemohon} dengan detail:

                    🗓️ {tanggal_mulai_cuti} s.d. {tanggal_selesai_cuti}
                    📅 Total: {selama_hari} hari
                    🎯 Keperluan: {keperluan}
                    📄 Harap tandatangani formulir pengajuan cuti tersebut.
                    """

                frappe.get_doc({
                    "doctype": "OIMS Notification",
                    "title": "Tanda Tangan Pengajuan Pengajuan Cuti",
                    "description": description_penerima.strip(),
                    "user": user_id_penerima,
                    "type": "Cuti",
                    "link_to": f"/pengajuan-cuti/{name}",
                    "link_to_label": "Tandatangani Formulir"
                }).insert(ignore_permissions=True)
            elif action == "reject":
                user_id_penerima = employee_data.user_id
                nama_pemohon = employee_data.nama_lengkap
                tanggal_mulai_cuti = doc.tanggal_mulai_cuti
                tanggal_selesai_cuti = doc.tanggal_selesai_cuti
                selama_hari = doc.selama_hari
                keperluan = doc.keperluan

                description_penerima = f"""
                    [{name}] Pengajuan Surat Cuti anda ditolak dengan detail:

                    🗓️ {tanggal_mulai_cuti} s.d. {tanggal_selesai_cuti}
                    📅 Total: {selama_hari} hari
                    🎯 Keperluan: {keperluan}
                    📄 Harap tandatangani formulir pengajuan cuti tersebut.
                    """

                frappe.get_doc({
                    "doctype": "OIMS Notification",
                    "title": "Tanda Tangan Pengajuan Pengajuan Cuti",
                    "description": description_penerima.strip(),
                    "user": user_id_penerima,
                    "type": "Cuti",
                    "link_to": f"/pengajuan-cuti/{name}",
                    "link_to_label": "Tandatangani Formulir"
                }).insert(ignore_permissions=True)

        return response_success("Berhasil menandatangani approval pengajuan cuti.", data={"name": name})

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error sign_cuti_tahunan_approval: {str(e)}")
        return response_error("Terjadi kesalahan saat menandatangani approval.", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def is_employee_allow_to_make_cuti_tahunan() -> dict:
    try:
        user_id = frappe.session.user

        karyawan = frappe.db.get_value(
            'Karyawan',
            {'user_id': user_id},
            ['jabatan', 'nrp', 'divisi', 'posisi_site'],
            as_dict=True
        )

        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        jabatan_exists = bool(karyawan.get('jabatan'))
        nrp_exists = bool(karyawan.get('nrp'))
        divisi_exists = bool(karyawan.get('divisi'))
        posisi_site_exists = bool(karyawan.get('posisi_site'))
        is_complete = jabatan_exists and nrp_exists and divisi_exists and posisi_site_exists

        result = {
            "jabatan_exists": jabatan_exists,
            "nrp_exists": nrp_exists,
            "divisi_exists": divisi_exists,
            "posisi_site_exists": posisi_site_exists,
            "is_complete": is_complete
        }

        return response_success(
            "Berhasil cek detail pengajuan cuti.",
            data=result
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error is_employee_allow_to_make_cuti_tahunan: {str(e)}")
        return response_error("Terjadi kesalahan saat mengambil data pengajuan cuti.", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def is_hr_set_approval_for_cuti() -> dict:
    try:
        user_id = frappe.session.user

        karyawan = frappe.db.get_value(
            'Karyawan',
            {'user_id': user_id},
            ['divisi', 'posisi_site'],
            as_dict=True
        )

        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        if karyawan.posisi_site == "HO":
            # Cek manager di divisi terkait
            manager_exists = frappe.db.exists(
                "Karyawan",
                {"jabatan": "Manager", "divisi": karyawan.divisi, "status": "Aktif", "beri_akses_untuk_login_oims_app": 1}
            )

            # Cek General Manager (tanpa divisi)
            gm_exists = frappe.db.exists(
                "Karyawan",
                {"jabatan": "General Manager", "status": "Aktif", "beri_akses_untuk_login_oims_app": 1}
            )

            # Cek Direktur Operasional (tanpa divisi)
            do_exists = frappe.db.exists(
                "Karyawan",
                {"jabatan": "Direktur Operasional", "status": "Aktif", "beri_akses_untuk_login_oims_app": 1}
            )

            result = {
                "manager_exists": bool(manager_exists),
                "general_manager_exists": bool(gm_exists),
                "direktur_operasional_exists": bool(do_exists),
            }
            result["is_complete"] = all(result.values())
        else:
            # Approval: Site Manager, Project Manager, Direktur Operasional
            site_manager_exists = frappe.db.exists(
                "Karyawan",
                {"jabatan": "Site Manager", "projek": karyawan.posisi_site, "status": "Aktif", "beri_akses_untuk_login_oims_app": 1}
            )
            project_manager_exists = frappe.db.exists(
                "Karyawan",
                {"jabatan": "Project Manager", "projek": karyawan.posisi_site, "status": "Aktif", "beri_akses_untuk_login_oims_app": 1}
            )
            do_exists = frappe.db.exists(
                "Karyawan",
                {"jabatan": "Direktur Operasional", "status": "Aktif", "beri_akses_untuk_login_oims_app": 1}
            )
            result = {
                "site_manager_exists": bool(site_manager_exists),
                "project_manager_exists": bool(project_manager_exists),
                "direktur_operasional_exists": bool(do_exists),
            }
            result["is_complete"] = all(result.values())

        return response_success("Berhasil cek struktur approval pengajuan cuti.", data=result)
    except Exception as e:
        frappe.log_error(f"Error is_hr_set_approval_for_cuti: {str(e)}")
        return response_error("Gagal mengambil struktur approval untuk pengajuan cuti.", http_status_code=500)

__all__ = [
    "get_all_self_cuti",
    "create_cuti_tahunan",
    "get_cuti_tahunan_detail",
    "get_approval_rights",
    "sign_cuti_tahunan_approval",
    "is_employee_allow_to_make_cuti_tahunan",
    "is_hr_set_approval_for_cuti"
]
