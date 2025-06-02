import frappe
from oims.api.responseHelper import response_success, response_error
from datetime import datetime, date

@frappe.whitelist(methods=["GET"])
def get_projects_that_has_roster() -> dict:
    try:
        unique_projects = frappe.db.sql("""
            SELECT DISTINCT
                rk.projek AS name,
                p.tanggal_dimulai,
                p.tanggal_berakhir
            FROM `tabRoster Kerja` rk
            JOIN `tabProjek` p ON rk.projek = p.name
            WHERE rk.projek IS NOT NULL
        """, as_dict=True)


        return response_success("Projects with rosters retrieved successfully", data=unique_projects)
    except Exception as e:
        frappe.log_error(f"Error retrieving projects with rosters: {str(e)}")
        return response_error("Failed to retrieve projects with rosters", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def get_employees_with_roster(project_name: str, from_date: str, to_date: str) -> dict:
    from datetime import datetime, date

    try:
        employees = frappe.get_all(
            "Karyawan",
            fields=["name", "nama_lengkap", "jabatan"],
            filters={"status": "Aktif"},
        )

        all_rosters = frappe.get_all(
            "Roster Kerja",
            filters={
                "tanggal_mulai": ["<=", to_date],
            },
            fields=["name", "projek", "karyawan", "tanggal_mulai", "tanggal_berakhir", "status"]
        )

        def parse_date(date_val):
            if not date_val:
                return None
            if isinstance(date_val, (datetime, date)):
                return datetime.combine(date_val, datetime.min.time()) if isinstance(date_val, date) and not isinstance(date_val, datetime) else date_val
            return datetime.strptime(date_val, "%Y-%m-%d")

        from_date_dt = parse_date(from_date)
        to_date_dt = parse_date(to_date)

        result = []
        for employee in employees:
            emp_rosters = [r for r in all_rosters if str(r.karyawan) == str(employee.name)]
            roster_status = None
            roster_status_message = None

            # Cek status cuti (prioritas utama)
            for roster in emp_rosters:
                mulai = parse_date(roster.tanggal_mulai)
                akhir = parse_date(roster.tanggal_berakhir)
                if roster.status == "Cuti":
                    if mulai and mulai <= to_date_dt and (not akhir or akhir >= from_date_dt):
                        roster_status = "Cuti"
                        roster_status_message = "Karyawan sedang cuti"
                        break

            # Jika tidak cuti, cek kerja di projek lain
            if not roster_status:
                for roster in emp_rosters:
                    mulai = parse_date(roster.tanggal_mulai)
                    akhir = parse_date(roster.tanggal_berakhir)
                    if roster.status == "Kerja" and roster.projek != project_name:
                        if mulai and mulai <= to_date_dt:
                            # Jika tanggal_berakhir None, berarti masih aktif
                            # Jika tanggal_berakhir >= from_date, berarti masih aktif di periode request
                            # Jika tanggal_berakhir < from_date, berarti sudah SELESAI sebelum periode request
                            if not akhir or akhir > from_date_dt:
                                roster_status = "Kerja"
                                roster_status_message = "Karyawan sedang bekerja di projek/site lain"
                                break

            result.append({
                "name": employee.name,
                "nama_lengkap": employee.nama_lengkap,
                "jabatan": employee.jabatan,
                "roster_status": roster_status,
                "roster_status_message": roster_status_message,
                "rosters": emp_rosters
            })

        return response_success("Employees with roster status retrieved successfully", data=result)

    except Exception as e:
        frappe.log_error(f"Error retrieving employees with roster status for project {project_name}: {str(e)}")
        return response_error("Failed to retrieve employees with roster status", http_status_code=500)

@frappe.whitelist(methods=["POST"])
def create_roster(projek: str, rosters: list) -> dict:
	try:
		if not projek or not rosters:
			return response_error("Project and roster data are required.", http_status_code=400)

		for roster in rosters:
			if not roster["karyawan"] or not roster["tanggal_mulai"]:
				return response_error("Karyawan and tanggal_mulai are required for each roster.", http_status_code=400)
			print(f"Creating roster for project {projek} for employee {roster['karyawan']} from {roster['tanggal_mulai']}")

			# Create the Roster Kerja document
			new_roster = frappe.get_doc({
				"doctype": "Roster Kerja",
				"projek": projek,
				"karyawan": roster["karyawan"],
				"tanggal_mulai": roster["tanggal_mulai"],
				"tanggal_berakhir": roster["tanggal_berakhir"] if "tanggal_berakhir" in roster else None,
				"status": roster["status"] if "status" in roster else "Aktif",
			})
			new_roster.insert()

		frappe.db.commit()
		return response_success("Roster created successfully", data={"project": projek, "rosters": rosters})

	except Exception as e:
		frappe.log_error(f"Error creating roster for project {projek}: {str(e)}")
		return response_error("Failed to create roster", http_status_code=500)

@frappe.whitelist(methods=["GET"])
def get_roster_by_project(project_name: str, from_date: str, to_date: str) -> dict:
    from datetime import datetime

    try:
        # 1. Ambil semua roster untuk projek tersebut (1x fetch saja)
        all_rosters = frappe.get_all(
            "Roster Kerja",
            filters={"projek": project_name},
            fields=["name", "projek", "karyawan", "tanggal_mulai", "tanggal_berakhir", "status"]
        )

        if not all_rosters:
            return response_error("No rosters found for this project.", http_status_code=404)

        # 2. Ambil daftar karyawan unik dari roster
        employee_map = {}
        for roster in all_rosters:
            emp_id = str(roster.karyawan)
            if emp_id not in employee_map:
                emp = frappe.get_value(
                    "Karyawan",
                    emp_id,
                    ["name", "nama_lengkap", "jabatan"],
                    as_dict=True
                )
                employee_map[emp_id] = {
                    "name": emp.name if emp else "",
                    "nama_lengkap": emp.nama_lengkap if emp else "",
                    "jabatan": emp.jabatan if emp else "",
                    "rosters": []
                }

        # 3. Parse tanggal
        from_dt = datetime.strptime(from_date, "%Y-%m-%d").date()
        to_dt = datetime.strptime(to_date, "%Y-%m-%d").date()

        # 4. Isi rosters yang masuk rentang tanggal
        for roster in all_rosters:
            emp_id = str(roster.karyawan)
            start_date = roster.tanggal_mulai
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if from_dt <= start_date <= to_dt:
                employee_map[emp_id]["rosters"].append({
                    "name": roster.name,
                    "projek": roster.projek,
                    "tanggal_mulai": roster.tanggal_mulai,
                    "tanggal_berakhir": roster.tanggal_berakhir,
                    "status": roster.status
                })

        # 5. Return hasil
        employees = list(employee_map.values())
        return response_success("Rosters retrieved successfully", data=employees)

    except Exception as e:
        frappe.log_error(f"Error retrieving roster for project {project_name}: {str(e)}")
        return response_error("Failed to retrieve roster", http_status_code=500)

__all__ = [
    "get_employees_with_roster",
    "get_projects_that_has_roster",
    "get_roster_by_project",
    "create_roster"
]
