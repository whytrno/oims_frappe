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

@frappe.whitelist(methods=["GET"], allow_guest=True)
def get_active_employee() -> dict:
    try:
        employee = frappe.db.get_all(
            "Karyawan",
            {"status": "Aktif"},
            [
                "name",
                "nrp",
                "nama_lengkap",
                "jabatan",
                "user_id",
            ],
        )
        return response_success("Current employee info retrieved successfully", data=employee)
    except Exception as e:
        frappe.log_error(f"Error retrieving current employee info: {str(e)}")
        return response_error("Failed to retrieve employee info", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def is_employee_is_make_signature() -> dict:
    try:
        current_user = frappe.session.user
        employee = frappe.db.get_value(
            "Karyawan",
            {"user_id": current_user, "status": "Aktif"},
            ["ttd"],
            as_dict=True,
        )

        is_make_signature = bool(employee and employee.get("ttd"))

        return response_success("Current employee info retrieved successfully",data=is_make_signature)
    except Exception as e:
        frappe.log_error(f"Error retrieving current employee info: {str(e)}")
        return response_error("Failed to retrieve employee info", http_status_code=500)

@frappe.whitelist(methods=["POST"])
def update_self_signature(ttd: str) -> dict:
    try:
        current_user = frappe.session.user
        employee = frappe.db.get_value(
            "Karyawan",
            {"user_id": current_user, "status": "Aktif"},
            "name",
        )
        if not employee:
            return response_error("User saat ini tidak terdaftar sebagai Karyawan Aktif", http_status_code=404)

        frappe.db.set_value("Karyawan", employee, "ttd", ttd)
        frappe.db.commit()

        return response_success("TTD berhasil diperbarui")
    except Exception as e:
        frappe.log_error(f"Error updating TTD: {str(e)}")
        return response_error("Gagal memperbarui TTD", http_status_code=500)


@frappe.whitelist(methods=["GET"])
def get_user_roles() -> dict:
    try:
        current_user = frappe.session.user
        roles = frappe.get_roles(current_user)
        return response_success("User roles retrieved successfully", data=roles)
    except Exception as e:
        frappe.log_error(f"Error retrieving user roles: {str(e)}")
        return response_error("Failed to retrieve user roles", http_status_code=500)

__all__ = [
    "get_current_employee_info",
    "get_active_employee",
    "is_employee_is_make_signature",
    "update_self_signature",
    "get_user_roles",
]
