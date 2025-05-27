import frappe
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist(methods=["GET"])
def get_current_employee_info() -> dict:
    try:
        current_user = frappe.session.user
        employee = frappe.db.get_value(
            "Karyawan",
            {"user_id": current_user, "status": "Aktif"},
            [
                "name",
                "nrp",
                "nama_lengkap",
                "jabatan",
                "user_id",
            ],
            as_dict=True,
        )
        return response_success("Current employee info retrieved successfully", data=employee)
    except Exception as e:
        frappe.log_error(f"Error retrieving current employee info: {str(e)}")
        return response_error("Failed to retrieve employee info", http_status_code=500)


__all__ = [
    "get_current_employee_info",
]
