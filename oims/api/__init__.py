import frappe
from frappe import _
from frappe.model import get_permitted_fields
from frappe.model.workflow import get_workflow_name
from frappe.query_builder import Order
from frappe.utils import add_days, date_diff, getdate, strip_html
from datetime import datetime
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm, Cm

SUPPORTED_FIELD_TYPES = [
    "Link",
    "Select",
    "Small Text",
    "Text",
    "Long Text",
    "Text Editor",
    "Table",
    "Check",
    "Data",
    "Float",
    "Int",
    "Section Break",
    "Date",
    "Time",
    "Datetime",
    "Currency",
    "Attach Image",
]


@frappe.whitelist()
def get_current_user_info() -> dict:
    current_user = frappe.session.user
    user = frappe.db.get_value(
        "User", current_user, ["name", "first_name", "full_name", "user_image"], as_dict=True
    )
    user["roles"] = frappe.get_roles(current_user)

    return user

# @frappe.whitelist()
# def submit_attendance(karyawan, lokasi_absen, foto, tipe, keterangan, waktu_absen, latitude, longitude, ambil_jatah_makan=False, izin=False):
#     """
#     Submit attendance for an employee.

#     :param employee: The name of the employee.
#     :param location: The location of the attendance.
#     :param photo_url: The URL of the photo taken during attendance.
#     :param attendance_type: The type of attendance (e.g., check-in, check-out).
#     :param timestamp: The timestamp of the attendance.
#     :param latitude: The latitude of the attendance location.
#     :param longitude: The longitude of the attendance location.
#     :param take_meal_allowance: Boolean indicating if meal allowance is taken.
#     :return: A dictionary containing the attendance details.
#     """
#     # Cek jika sudah absen dari tipe yang sama di hari ini
#     today = datetime.today().date()
#     existing_attendance = frappe.db.exists(
#         "Absensi",
#         {
#             "karyawan": karyawan,
#             "tipe": tipe,
#             "waktu_absen": ["like", f"{today}%"]
#         }
#     )
#     if existing_attendance:
#         frappe.throw(_("Anda sudah absen {tipe} hari ini."))

#     attendance_doc = frappe.get_doc({
#         "doctype": "Absensi",
#         "karyawan": karyawan,
#         "lokasi_absen": lokasi_absen,
#         "foto": foto,
#         "tipe": tipe,
#         "keterangan": keterangan,
#         "waktu_absen": waktu_absen,
#         "latitude": latitude,
#         "longitude": longitude,
#         "ambil_jatah_makan": ambil_jatah_makan,
#         "izin": izin
#     })
#     attendance_doc.save()
#     frappe.logger().info(f"Attendance submitted for {karyawan} at {waktu_absen}")
#     return attendance_doc.as_dict()

# from datetime import datetime

@frappe.whitelist()
def submit_attendance(karyawan, lokasi_absen, foto, tipe, keterangan, waktu_absen, latitude, longitude, ambil_jatah_makan=False, izin=False):
    """
    Submit attendance for an employee with error handling and logging.
    """
    try:
        # Cek jika sudah absen dari tipe yang sama di hari ini
        today = datetime.today().date()
        existing_attendance = frappe.db.exists(
            "Absensi",
            {
                "karyawan": karyawan,
                "tipe": tipe,
                "waktu_absen": ["like", f"{today}%"]
            }
        )
        if existing_attendance:
            frappe.throw(_("Anda sudah absen {tipe} hari ini."))

        # Buat dokumen Absensi
        attendance_doc = frappe.get_doc({
            "doctype": "Absensi",
            "karyawan": karyawan,
            "lokasi_absen": lokasi_absen,
            "foto": foto,
            "tipe": tipe,
            "keterangan": keterangan,
            "waktu_absen": waktu_absen,
            "latitude": latitude,
            "longitude": longitude,
            "ambil_jatah_makan": ambil_jatah_makan,
            "izin": izin
        })

        # Simpan dokumen ke database
        attendance_doc.save()

        # Catat log sukses (info log, bukan error)
        frappe.logger().info(f"Attendance successfully submitted for {karyawan} at {waktu_absen}")
        return attendance_doc.as_dict()

    except frappe.ValidationError as e:
        # Tangkap dan catat error validasi
        frappe.log_error(title='Validation Error in Attendance', message=str(e))
        frappe.logger().error(f"Validation error for attendance submission: {str(e)}")
        frappe.throw(_("Terjadi kesalahan validasi: {0}").format(str(e)))

    except Exception as e:
        # Tangkap dan catat error yang tidak terduga
        frappe.log_error(title='Unexpected Error in Attendance Submission', message=frappe.get_traceback())
        frappe.logger().error(f"Unexpected error during attendance submission: {str(e)}", exc_info=True)
        frappe.throw(_("Terjadi kesalahan yang tidak terduga: {0}").format(str(e)))



@frappe.whitelist()
def get_attendance_calendar_events(employee: int, from_date: str, to_date: str) -> dict[str, str]:
    holidays = []
    attendance = get_attendance_for_calendar(employee, from_date, to_date)
    events = {}

    date = getdate(from_date)
    while date_diff(to_date, date) >= 0:
        date_str = date.strftime("%Y-%m-%d")
        if date in holidays:
            events[date_str] = "Holiday"
        elif date in attendance:
            events[date_str] = attendance[date]
        date = add_days(date, 1)

    return events

# def get_holidays_for_calendar(employee: str, from_date: str, to_date: str) -> list[str]:
# 	if holiday_list := get_holiday_list_for_employee(employee, raise_exception=False):
# 		return frappe.get_all(
# 			"Holiday",
# 			filters={"parent": holiday_list, "holiday_date": ["between", [from_date, to_date]]},
# 			pluck="holiday_date",
# 		)

# 	return []



def get_attendance_for_calendar(employee: str, from_date: str, to_date: str) -> list[dict[str, str]]:
    attendance = frappe.get_all(
        "Absensi",
        {"karyawan": employee, "waktu_absen": ["between", [from_date, to_date]], "tipe": ["!=", "Out"]},
        ["waktu_absen", "tipe", "izin", "telat"],
    )

    for att in attendance:
        # ubah time datetime ke date
        att["attendance_date"] = att["waktu_absen"].date()

        if att["izin"]:
            att["status"] = "Izin"
        elif att["telat"]:
            att["status"] = "Telat"
        elif att["tipe"] == "In":
            att["status"] = "Tepat Waktu"

    data = {d["attendance_date"]: d["status"] for d in attendance}
    print(f'data: {data}')

    return {d["attendance_date"]: d["status"] for d in attendance}


@frappe.whitelist()
def create_folders_if_not_exist(base_path, folder_path):
    # Pisahkan path menjadi komponen folder
    folders = folder_path.split('/')

    # Variable untuk melacak full path dari folder
    current_folder = base_path

    # Loop melalui setiap folder di path
    for folder in folders:
        current_folder = f"{current_folder}/{folder}"

        # Jika folder belum ada, buat folder baru
        if not frappe.db.exists('File', current_folder):
            folder_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": "Home/absensi",
                "folder": base_path if current_folder == f"{base_path}/{folder}" else current_folder.rsplit('/', 1)[0],
                "is_folder": 1,
                # "is_private": 1
            })
            folder_doc.save()
            frappe.logger().info(f"Folder '{folder}' created in '{current_folder}'")


@frappe.whitelist()
def get_current_employee_info() -> dict:
    current_user = frappe.session.user
    print(f"current_user: {current_user}")
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
    return employee

import frappe

@frappe.whitelist()
def get_private_file(filename):
    """Mengembalikan file dari folder private files"""
    file_path = f"private/files/{filename}"

    # Pastikan file ada di sistem
    if not frappe.utils.file_manager.exists(file_path):
        frappe.throw("File tidak ditemukan", frappe.DoesNotExistError)

    # Kembalikan sebagai response file
    return frappe.utils.response.download_private_file(file_path)


@frappe.whitelist()
def get_all_employees() -> list[dict]:
    return frappe.get_all(
        "Karyawan",
        fields=["*"],
        limit=999999,
    )

@frappe.whitelist()
def get_all_surat_tugas() -> list[dict]:
    return frappe.get_all(
        "Surat Tugas",
        fields=["*"],
        limit=999999,
    )

@frappe.whitelist()
def get_surat_tugas_detail(name: str) -> dict:
	return frappe.get_doc("Surat Tugas", name).as_dict()

def get_surat_tugas_doc_file_fun(name: str):
    surat_tugas = frappe.get_doc("Surat Tugas", name)
    doc_name_final = surat_tugas.name.replace("/", "_")
    doc_url = f"{doc_name_final} - {surat_tugas.site}.docx"
    file_record = frappe.get_all(
        "File",
        filters={"file_name": ["like", f"%{doc_url}%"]},
        fields=["name", "file_url"],
        limit=1,
    )

    return file_record[0]["file_url"]

@frappe.whitelist()
def get_surat_tugas_doc_file(name: str) -> dict:
    file_url = get_surat_tugas_doc_file_fun(name)

    if file_url:
        return {"file_url": file_url}

    return {"error": "File not found"}

@frappe.whitelist()
def sign_surat_tugas(name: str, employeeName) -> dict:
    file_url = get_surat_tugas_doc_file_fun(name)
    if not file_url:
        return {"error": "File not found"}

    user_signature = frappe.db.get_value("Karyawan", employeeName, "tanda_tangan")
    if not user_signature:
        return {"error": "User signature not found"}

    # jika user_signature tidak ada kata private di string user_signature, maka tambahkan kata /public
    if "private" not in user_signature:
        user_signature = "/public" + user_signature

    docx_local_path = frappe.get_site_path() + '/public' + file_url
    signature_png_path = frappe.get_site_path() + user_signature

    docxFile = DocxTemplate(docx_local_path)

    image = InlineImage(docxFile, signature_png_path, width=Cm(6) , height=Cm(3))
    context = {
		'ttd': image
	}
    docxFile.render(context)

    full_output_path = docx_local_path

    docxFile.save(full_output_path)

    return {"file_url": docx_local_path}


@frappe.whitelist()
def is_employee_add_signature(name) -> bool:
    tanda_tangan = frappe.db.get_value("Karyawan", name, "tanda_tangan")
    return bool(tanda_tangan)

# HR Settings
@frappe.whitelist()
def get_hr_settings() -> dict:
    settings = frappe.db.get_singles_dict("HR Settings", cast=True)
    return frappe._dict(
        allow_employee_checkin_from_mobile_app=settings.allow_employee_checkin_from_mobile_app,
        allow_geolocation_tracking=settings.allow_geolocation_tracking,
    )


# Notifications
@frappe.whitelist()
def get_unread_notifications_count() -> int:
    return frappe.db.count(
        "PWA Notification",
        {"to_user": frappe.session.user, "read": 0},
    )


@frappe.whitelist()
def mark_all_notifications_as_read() -> None:
    frappe.db.set_value(
        "PWA Notification",
        {"to_user": frappe.session.user, "read": 0},
        "read",
        1,
        update_modified=False,
    )


@frappe.whitelist()
def are_push_notifications_enabled() -> bool:
    try:
        return frappe.db.get_single_value("Push Notification Settings", "enable_push_notification_relay")
    except frappe.DoesNotExistError:
        # push notifications are not supported in the current framework version
        return False


# Company
@frappe.whitelist()
def get_company_currencies() -> dict:
    Company = frappe.qb.DocType("Company")
    Currency = frappe.qb.DocType("Currency")

    query = (
        frappe.qb.from_(Company)
        .join(Currency)
        .on(Company.default_currency == Currency.name)
        .select(
            Company.name,
            Company.default_currency,
            Currency.name.as_("currency"),
            Currency.symbol.as_("symbol"),
        )
    )

    companies = query.run(as_dict=True)
    return {company.name: (company.default_currency, company.symbol) for company in companies}


@frappe.whitelist()
def get_currency_symbols() -> dict:
    Currency = frappe.qb.DocType("Currency")

    currencies = (frappe.qb.from_(Currency).select(Currency.name, Currency.symbol)).run(as_dict=True)

    return {currency.name: currency.symbol or currency.name for currency in currencies}


@frappe.whitelist()
def get_company_cost_center_and_expense_account(company: str) -> dict:
    return frappe.db.get_value(
        "Company", company, ["cost_center", "default_expense_claim_payable_account"], as_dict=True
    )


# Form View APIs
@frappe.whitelist()
def get_doctype_fields(doctype: str) -> list[dict]:
    fields = frappe.get_meta(doctype).fields
    return [
        field
        for field in fields
        if field.fieldtype in SUPPORTED_FIELD_TYPES and field.fieldname != "amended_from"
    ]


@frappe.whitelist()
def get_doctype_states(doctype: str) -> dict:
    states = frappe.get_meta(doctype).states
    return {state.title: state.color.lower() for state in states}


# File
@frappe.whitelist()
def get_attachments(dt: str, dn: str):
    from frappe.desk.form.load import get_attachments

    return get_attachments(dt, dn)


@frappe.whitelist()
def upload_base64_file(content, filename, dt=None, dn=None, fieldname=None):
    import base64
    import io
    from mimetypes import guess_type

    from PIL import Image, ImageOps

    from frappe.handler import ALLOWED_MIMETYPES

    decoded_content = base64.b64decode(content)
    content_type = guess_type(filename)[0]
    if content_type not in ALLOWED_MIMETYPES:
        frappe.throw(_("You can only upload JPG, PNG, PDF, TXT or Microsoft documents."))

    if content_type.startswith("image/jpeg"):
        # transpose the image according to the orientation tag, and remove the orientation data
        with Image.open(io.BytesIO(decoded_content)) as image:
            transpose_img = ImageOps.exif_transpose(image)
            # convert the image back to bytes
            file_content = io.BytesIO()
            transpose_img.save(file_content, format="JPEG")
            file_content = file_content.getvalue()
    else:
        file_content = decoded_content

    return frappe.get_doc(
        {
            "doctype": "File",
            "attached_to_doctype": dt,
            "attached_to_name": dn,
            "attached_to_field": fieldname,
            "folder": "Home",
            "file_name": filename,
            "content": file_content,
            # "is_private": 1,
        }
    ).insert()


@frappe.whitelist()
def delete_attachment(filename: str):
    frappe.delete_doc("File", filename)


@frappe.whitelist()
def download_salary_slip(name: str):
    import base64

    from frappe.utils.print_format import download_pdf

    default_print_format = frappe.get_meta("Salary Slip").default_print_format or "Standard"

    try:
        download_pdf("Salary Slip", name, format=default_print_format)
    except Exception:
        frappe.throw(_("Failed to download Salary Slip PDF"))

    base64content = base64.b64encode(frappe.local.response.filecontent)
    content_type = frappe.local.response.type

    return f"data:{content_type};base64," + base64content.decode("utf-8")


# Workflow
@frappe.whitelist()
def get_workflow(doctype: str) -> dict:
    workflow = get_workflow_name(doctype)
    if not workflow:
        return frappe._dict()
    return frappe.get_doc("Workflow", workflow)


def get_workflow_state_field(doctype: str) -> str | None:
    workflow_name = get_workflow_name(doctype)
    if not workflow_name:
        return None

    override_status, workflow_state_field = frappe.db.get_value(
        "Workflow",
        workflow_name,
        ["override_status", "workflow_state_field"],
    )
    # NOTE: checkbox labelled 'Don't Override Status' is named override_status hence the inverted logic
    if not override_status:
        return workflow_state_field
    return None


def get_allowed_states_for_workflow(workflow: dict, user_id: str) -> list[str]:
    user_roles = frappe.get_roles(user_id)
    return [transition.state for transition in workflow.transitions if transition.allowed in user_roles]


# Permissions
@frappe.whitelist()
def get_permitted_fields_for_write(doctype: str) -> list[str]:
    return get_permitted_fields(doctype, permission_type="write")


# Lokasi Site
@frappe.whitelist()
def get_all_lokasi_absen() -> list[dict]:
    return frappe.get_all(
        "Lokasi Absen",
        fields=["nama", "latitude", "longitude", "radius"],
        limit=999999,
    )

# Hazard Report
@frappe.whitelist()
def get_all_hazard_report() -> list[dict]:
    Report = frappe.qb.DocType("Hazard Report")
    Photo = frappe.qb.DocType("Hazard Report Image")

    # Ambil semua data dari query
    query = (
        frappe.qb.from_(Report)
        .join(Photo)
        .on(Report.name == Photo.parent)
        .select(
            Report.name,
            Report.waktu,
            Report.kode_bahaya,
            Report.kategori_temuan,
            Report.site,
            Report.status_temuan,
            Photo.foto,
            Photo.jenis,
        )
    )

    raw_data = query.run(as_dict=True)

    reports = {}

    for row in raw_data:
        report_name = row["name"]

        if report_name not in reports:
            reports[report_name] = {
                "name": report_name,
                "waktu": row["waktu"],
                "kode_bahaya": row["kode_bahaya"],
                "kategori_temuan": row["kategori_temuan"],
                "site": row["site"],
                "status_temuan": row["status_temuan"],
                "status_tindakan": "Belum ada tindakan",
                "foto": [],
            }

        if row["jenis"] == "Tindakan":
            reports[report_name]["status_tindakan"] = "Sudah ditindaklanjuti"
        elif row["jenis"] == "Temuan" and reports[report_name]["status_tindakan"] != "Sudah ditindaklanjuti":
            reports[report_name]["status_tindakan"] = "Masih temuan"

        reports[report_name]["foto"].append({
            "jenis": row["jenis"],
            "foto": row["foto"],
        })

    reports = dict(sorted(reports.items(), key=lambda x: x[1]["waktu"], reverse=True))

    return list(reports.values())

# Inspection Activity
@frappe.whitelist()
def get_all_inspection_activities() -> list[dict]:
    Inspection = frappe.qb.DocType("Inspection Activities")
    Photo = frappe.qb.DocType("Inspection Activitiy Images")

    query = (
        frappe.qb.from_(Inspection)
        .join(Photo)
        .on(Inspection.name == Photo.parent)
        .select(
            Inspection.name,
            Inspection.site,
            Inspection.waktu,
            Inspection.keterangan_hasil_inspeksi,
            Photo.foto,
        )
    )

    raw_data = query.run(as_dict=True)

    inspections = {}

    for row in raw_data:
        name = row["name"]

        if name not in inspections:
            inspections[name] = {
                "name": name,
                "site": row["site"],
                "waktu": row["waktu"],
                "keterangan_hasil_inspeksi": row["keterangan_hasil_inspeksi"],
                "foto": [],
            }

        inspections[name]["foto"].append({
            "foto": row["foto"],
        })

    inspections = dict(sorted(inspections.items(), key=lambda x: x[1]["waktu"], reverse=True))

    return list(inspections.values())

# Jumlah Makan
@frappe.whitelist()
def get_today_karyawan_makan() -> list[dict]:
    return frappe.get_all(
        "Absensi",
        {
            "ambil_jatah_makan": 1,
            "creation": [">=", datetime.today().date()],
        },
        ["karyawan.nama_lengkap as nama_karyawan"],
        limit=999999,
    )

@frappe.whitelist()
def upload_files_to_hazard_report_child_table(name: str, files: list, jenis: str):
    sales_invoice = frappe.get_doc("Hazard Report", name)

    for file in files:
        sales_invoice.append("foto", {
            "jenis": jenis,
            "foto": file,
        })

    sales_invoice.save()

@frappe.whitelist()
def upload_files_to_inspection_activity_child_table(name: str, files: list):
    sales_invoice = frappe.get_doc("Inspection Activities", name)

    for file in files:
        sales_invoice.append("foto", {
            "foto": file,
        })

    sales_invoice.save()
