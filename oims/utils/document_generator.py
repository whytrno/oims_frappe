import frappe
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import os
import base64
import uuid

def generate_docx_from_template(
    template_path, context, output_name, images_context=None
):
    """
    Generate docx file from template with given context and inline images.
    """
    doc = DocxTemplate(template_path)

    # Add images to context if provided
    if images_context:
        context.update(images_context)

    doc.render(context)
    output_path = frappe.utils.get_site_path('private', 'files', output_name)
    doc.save(output_path)
    return output_path

def upload_to_file_manager(doc_file, doc_name, surat_type, year=None, month=None):
    """
    Upload file to Frappe File Manager under structured folder, and return file_url.
    surat_type: e.g., 'Surat Tugas', 'Cuti Tahunan'
    """
    with open(doc_file, "rb") as f:
        file_data = f.read()

    year = year or frappe.utils.nowdate().split('-')[0]
    month = month or frappe.utils.formatdate(frappe.utils.nowdate(), "MM")

    folder_structure = f"Surat/{surat_type}/{year}/{month}"
    create_folders_if_not_exist("Home", folder_structure)

    final_folder = f"Home/{folder_structure}"

    _file = frappe.get_doc({
        "doctype": "File",
        "file_name": doc_name,
        "folder": final_folder,
        "content": file_data,
        "ignore_duplicate_entry_error": True,
    })
    _file.save()
    file_url = _file.file_url

    # Clean up temp
    if os.path.exists(doc_file):
        os.remove(doc_file)

    return file_url

def create_folders_if_not_exist(base_path, folder_path):
    folders = folder_path.split('/')
    current_folder = base_path
    for folder in folders:
        current_folder = f"{current_folder}/{folder}"
        if not frappe.db.exists('File', current_folder):
            folder_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": folder,
                "folder": base_path if current_folder == f"{base_path}/{folder}" else current_folder.rsplit('/', 1)[0],
                "is_folder": 1,
            })
            folder_doc.save()

def formatdate_indonesia(date_str):
    bulan = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    date_obj = frappe.utils.getdate(date_str)
    tanggal = date_obj.day
    bulan_indonesia = bulan[date_obj.month]
    tahun = date_obj.year
    return f"{tanggal} {bulan_indonesia} {tahun}"

def formatdate_indonesia_with_day(date_str):
    hari = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    bulan = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
    date_obj = frappe.utils.getdate(date_str)
    hari_indonesia = hari[date_obj.weekday()]
    tanggal = date_obj.day
    bulan_indonesia = bulan[date_obj.month]
    tahun = date_obj.year
    return f"{hari_indonesia}, {tanggal} {bulan_indonesia} {tahun}"

def build_inline_image(doc, path, width=80, height=50):
    if path and os.path.exists(path):
        return InlineImage(doc, path, width=Mm(width), height=Mm(height))
    return ''

def save_base64_signature_to_file(base64_str, prefix="ttd"):
    # Expecting format: "data:image/png;base64,...."
    if not base64_str or ',' not in base64_str:
        return None
    header, encoded = base64_str.split(',', 1)
    ext = ".png"
    file_name = f"{prefix}_{uuid.uuid4().hex}{ext}"
    file_path = frappe.utils.get_site_path('private', 'files', file_name)
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(encoded))
    return file_path
