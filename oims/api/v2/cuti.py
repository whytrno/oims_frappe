import frappe
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist()
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
            "Cuti Tahunan",
            fields=["name", "karyawan_pemohon", "keperluan", "karyawan_penerima_job_pending", "tanggal_mulai_cuti", "tanggal_selesai_cuti", "selama_hari"],
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

            cuti["status"] = "Proses"

        return response_success("Berhasil mengambil data lokasi cuti tahunan.", data=data)
    except Exception as e:
        return response_error("Terjadi kesalahan saat mengambil data cuti tahunan.", http_status_code=500)

__all__ = [
    "get_all_self_cuti",
]
