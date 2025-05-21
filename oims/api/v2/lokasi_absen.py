import frappe
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist()
def get_all_lokasi_absen() -> list[dict]:
    try:
        data = frappe.get_all(
            "Lokasi Absen",
            fields=["name", "nama", "projek", "latitude", "longitude", "radius"],
            limit=999999,
        )
        return response_success("Berhasil mengambil data lokasi absen.", data=data)
    except Exception as e:
        return response_error("Terjadi kesalahan saat mengambil data absensi.", http_status_code=500)

__all__ = [
	"get_all_lokasi_absen",
]
