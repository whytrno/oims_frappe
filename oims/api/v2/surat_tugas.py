import frappe
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist(methods=["GET"])
def get_surat_tugas(is_signed_filter: bool | None = None) -> dict:
    try:
        filters = {}
        if is_signed_filter is not None:
            filters["sudah_di_tanda_tangani"] = int(is_signed_filter)

        surat_tugas = frappe.get_all(
            "Surat Tugas",
            filters=filters,
            fields=["name", "tanggal_berangkat", "sudah_di_tanda_tangani", "keperluan", "site", "status_penugasan"],
            limit=9999
        )

        for surat in surat_tugas:
            employee_id_on_surat = frappe.get_all(
                "Karyawan Surat Tugas",
                filters={"parent": surat.name},
                fields=["employee_id"],
            )
            karyawan_on_surat = []
            for employee in employee_id_on_surat:
                karyawan = frappe.get_value(
                    "Karyawan",
                    employee.employee_id,
                    ["nama_lengkap"],
                    as_dict=True
                )
                if karyawan:
                    karyawan_on_surat.append(karyawan.nama_lengkap)

            surat["karyawan"] = karyawan_on_surat

        return response_success("Data surat tugas retrieved successfully", data=surat_tugas)
    except Exception as e:
        frappe.log_error(f"Error retrieving surat tugas: {str(e)}")
        return response_error("Failed to retrieve surat tugas", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def get_surat_tugas_detail(name: str) -> dict:
    try:
        surat_tugas = frappe.get_doc("Surat Tugas", name)
        surat_tugas_data = {
            "name": surat_tugas.name,
            "tanggal_berangkat": surat_tugas.tanggal_berangkat,
            "site": surat_tugas.site,
            "keperluan": surat_tugas.keperluan,
            "sudah_di_tanda_tangani": surat_tugas.sudah_di_tanda_tangani,
            "status_penugasan": surat_tugas.status_penugasan,
            "doc_url": surat_tugas.doc_url,
        }

        karyawan_on_surat = []
        for employee in surat_tugas.karyawan:
            karyawan = frappe.get_value(
                "Karyawan",
                employee.employee_id,
                ["nama_lengkap"],
                as_dict=True
            )
            if karyawan:
                karyawan_on_surat.append(karyawan.nama_lengkap)

        surat_tugas_data["karyawan"] = karyawan_on_surat

        return response_success("Data surat tugas retrieved successfully", data=surat_tugas_data)
    except Exception as e:
        frappe.log_error(f"Error retrieving surat tugas detail: {str(e)}")
        return response_error("Failed to retrieve surat tugas detail", http_status_code=500)

__all__ = [
	"get_surat_tugas",
	"get_surat_tugas_detail",
]
