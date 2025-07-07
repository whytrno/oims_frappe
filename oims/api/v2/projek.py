import frappe
from frappe.utils import getdate
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist(methods=["GET"])
def get_all_project() -> list[dict]:
    try:
        data = frappe.db.get_value(
            'Projek',
            'name',
            as_dict=True
        )

        return response_success("Berhasil mengambil data projek.", data=data)
    except Exception as e:
        return response_error("Terjadi kesalahan saat mengambil data projek.", http_status_code=500)

__all__ = [
    "get_all_project",
]
