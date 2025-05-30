import frappe
from datetime import datetime
import base64
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist(methods=["POST"])
def absensi_process(lokasi_absen, foto, tipe, keterangan, latitude, longitude, ambil_jatah_makan=False):
    if not foto:
        return response_error("Foto tidak boleh kosong.", http_status_code=400)

    if "," in foto:
        foto = foto.split(",")[1]

    file_doc = None

    try:
        try:
            file_content = base64.b64decode(foto)
        except Exception as e:
            frappe.log_error(f"Error decoding base64 image: {str(e)}")
            return response_error("Format foto tidak valid.", http_status_code=400)

        # Ambil tanggal hari ini
        today = datetime.now()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        day = today.strftime("%d")

        # Tentukan folder target
        folder_path = f"Home/absensi/{year}/{month}/{day}"

        user_id = frappe.session.user

        karyawan = frappe.db.get_list(
            'Karyawan',
            filters={'user_id': user_id},
            fields=['name', 'nama_lengkap'],
            limit_page_length=1
        )

        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.", http_status_code=404)

        # Cek duplikat absensi
        existing_attendance = frappe.db.exists(
            "Absensi",
            {
                "karyawan": karyawan[0].name,
                "tipe": tipe,
                "waktu_absen": ["like", f"{today.date()}%"]
            }
        )

        if existing_attendance:
            return response_error(f"Anda sudah absen {tipe} hari ini.", http_status_code=400)

        # Pastikan folder absensi ada
        base = "Home"
        for part in ["absensi", year, month, day]:
            new_path = f"{base}/{part}"
            if not frappe.db.exists("File", {"file_name": part, "folder": base}):
                frappe.get_doc({
                    "doctype": "File",
                    "file_name": part,
                    "is_folder": 1,
                    "folder": base,
                    "is_private": 1
                }).insert(ignore_permissions=True)
            base = new_path

        # Simpan file
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{karyawan[0].nama_lengkap}-{tipe}-{day}{month}{year}.jpg",
            "content": file_content,
            "is_private": 0,
            "folder": folder_path
        })
        file_doc.insert(ignore_permissions=True)

        waktu_absen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lokasi_absen_final = "Ho - HO" if tipe == "Dinas Luar" else lokasi_absen

        # Simpan dokumen absensi
        attendance_doc = frappe.get_doc({
            "doctype": "Absensi",
            "karyawan": karyawan[0].name,
            "lokasi_absen": lokasi_absen_final,
            "foto": file_doc.file_url,
            "tipe": tipe,
            "keterangan": keterangan,
            "waktu_absen": waktu_absen,
            "latitude": latitude,
            "longitude": longitude,
            "ambil_jatah_makan": ambil_jatah_makan,
        })
        attendance_doc.save()

        return response_success(f"Anda berhasil absen dengan tipe: {tipe}.", attendance_doc)

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Gagal proses absensi")

        # Hapus file jika sudah dibuat tapi proses gagal
        if file_doc:
            try:
                file_doc.delete(ignore_permissions=True)
            except Exception as delete_error:
                frappe.log_error(f"Error deleting file on rollback: {str(delete_error)}")

        raise e  # Lempar ulang error agar ditangani di luar fungsi jika perlu

@frappe.whitelist(methods=["GET"])
def get_self_today_absen():
    from frappe.utils import nowdate

    try:
        user_id = frappe.session.user

        karyawan = frappe.db.get_value(
            'Karyawan',
            {'user_id': user_id},
            ['name', 'nama_lengkap'],
            as_dict=True
        )

        if not karyawan:
            return response_error("Data karyawan tidak ditemukan untuk user ini.")

        start = f"{nowdate()} 00:00:00"
        end = f"{nowdate()} 23:59:59"

        self_today_attendance = frappe.get_all(
            "Absensi",
            filters={
                "karyawan": karyawan.name,
                "waktu_absen": ["between", [start, end]]
            },
            fields=["tipe", "waktu_absen", "ambil_jatah_makan"],
            order_by="waktu_absen desc",
            limit=1
        )

        if not self_today_attendance:
            return response_error("Anda belum absen hari ini.", http_status_code=404)


        attendance_hour = self_today_attendance[0].waktu_absen.strftime("%H:%M:%S")
        self_today_attendance[0].waktu_absen = attendance_hour

        return response_success("Berhasil mengambil data absensi.", self_today_attendance[0])

    except Exception:
        frappe.log_error(frappe.get_traceback(), "get_self_today_absen error")
        return response_error("Terjadi kesalahan saat mengambil data absensi.", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def get_attendance_calendar_events(from_date, to_date):
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

        events = frappe.get_all(
            "Absensi",
            filters={
                "karyawan": karyawan.name,
                "waktu_absen": ["between", [from_date, to_date]]
            },
            fields=["tipe", "telat", "ambil_jatah_makan", "waktu_absen"],
            order_by="waktu_absen desc"
        )

        count = {
            "in": 0,
            "out": 0,
            "dinas_luar": 0,
            "izin_sakit": 0,
            "izin_lainnya": 0,
            "telat": 0,
            "ambil_jatah_makan": 0
        }

        for event in events:
            if event.tipe == "In":
                count["in"] += 1
            elif event.tipe == "Out":
                count["out"] += 1
            elif event.tipe == "Dinas Luar":
                count["dinas_luar"] += 1
            elif event.tipe == "Sakit":
                count["sakit"] += 1
            elif event.tipe == "Izin":
                count["izin"] += 1

            if event.telat:
                count["telat"] += 1
            if event.ambil_jatah_makan:
                count["ambil_jatah_makan"] += 1

        data = {
			"events": events,
			"count": count
		}

        return response_success("Berhasil mengambil data absensi.", data)

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "get_attendance_calendar_events error")
        return response_error("Terjadi kesalahan saat mengambil data absensi.", http_status_code=500)

__all__ = [
    "absensi_process",
    "get_self_today_absen",
    "get_attendance_calendar_events"
]
