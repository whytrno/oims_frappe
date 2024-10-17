# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import frappe
import os


class SuratMutasi(Document):
	def before_save(self):
		self.validate_karyawan_data()
		
		nama_surat_raw = self.no_surat.replace('/', '_')
		nama_surat_temp = f"{nama_surat_raw}_temp.docx"
		nama_surat = f"{nama_surat_raw}.docx"
		# penandatangan = frappe.get_doc('Karyawan', self.penanda_tangan)

		generated_docx = self.generate_document(nama_surat_temp)
		self.upload_document_to_file_manager(nama_surat, generated_docx)
	
	def validate_karyawan_data(self):
		errors = []
		if self.karyawan:
			karyawan_doc = frappe.get_doc('Karyawan', self.karyawan, ['nrp', 'divisi'])
			
			if not karyawan_doc.divisi:
				errors.append(f"User {karyawan_doc.nama_lengkap} belum mengisi divisi.")
			
			if not karyawan_doc.nrp:
				errors.append(f"User {karyawan_doc.nama_lengkap} belum mengisi NRP.")

		# If there are errors, prevent saving and display messages
		if errors:
			frappe.throw("<br>".join(errors), title="Validation Failed")
 
	def format_site_location(self, site_location):
		site_location_doc = frappe.get_doc('Projek', site_location)
		site_location_formatted = f'{site_location_doc.nama_projek}'
		if site_location_doc.lokasi_projek:
			site_location_formatted += f', {site_location_doc.lokasi_projek}'
   
		site_location_formatted = site_location_formatted.replace('&', '&amp;')
   
		return site_location_formatted

	def generate_document(self, nama_surat):
		tanggal_mutasi = self.formatdate_indonesia(self.tanggal_mutasi)
  
		tanggal_surat = frappe.utils.formatdate(frappe.utils.nowdate(), "dd MMMM yyyy")
   
		lokasi_site_awal = self.format_site_location(self.lokasi_site_awal)
		lokasi_site_tujuan = self.format_site_location(self.lokasi_site_tujuan)
		tanggal_surat_formatted = self.formatdate_indonesia(tanggal_surat)

		template_path = frappe.get_app_path('oims', 'templates', 'docs', 'surat_mutasi.docx')
		doc = DocxTemplate(template_path)

		return self.generate_single_document(doc, tanggal_mutasi, tanggal_surat_formatted, nama_surat, lokasi_site_awal, lokasi_site_tujuan)

		# pdf_file_path = frappe.utils.get_site_path('private', 'files', 'surat_keterangan.pdf')
		# pypandoc.convert_file(docx_file_path, 'pdf', outputfile=pdf_file_path)

	def generate_single_document(self, doc, tanggal_mutasi, tanggal_surat, nama_surat, lokasi_site_awal, lokasi_site_tujuan):
		karyawan_data = frappe.get_doc('Karyawan', self.karyawan)
		context = {
			'no_surat': self.no_surat,
			'tanggal': tanggal_surat,
			'nama': karyawan_data.nama_lengkap,
			'nrp': karyawan_data.nrp,
			'divisi': self.dari_divisi,
			'jabatan': karyawan_data.jabatan,
			'tanggal_mutasi': tanggal_mutasi,
			'ke_divisi': self.ke_divisi,
			'ke_jabatan': self.ke_jabatan,
			'lokasi_site_awal': lokasi_site_awal,
			'lokasi_site_tujuan': lokasi_site_tujuan,
		}

		# Render template
		doc.render(context)

		# Simpan dokumen yang dihasilkan
		docx_file_path = frappe.utils.get_site_path('private', 'files', nama_surat)
		doc.save(docx_file_path)

		return docx_file_path

	def create_folders_if_not_exist(self, base_path, folder_path):
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
					"file_name": folder,
					"folder": base_path if current_folder == f"{base_path}/{folder}" else current_folder.rsplit('/', 1)[0],
					"is_folder": 1,
					"is_private": 1
				})
				folder_doc.save()
				frappe.logger().info(f"Folder '{folder}' created in '{current_folder}'")

	def upload_document_to_file_manager(self, nama_surat, file):
		try:
			with open(file, 'rb') as f:
				file_data = f.read()

			# Get the current year and month in Roman numeral format
			year_now = frappe.utils.nowdate().split('-')[0]
			month_now_roman = frappe.utils.formatdate(frappe.utils.nowdate(), "MM")

			# Define the full folder path based on your structure
			folder_structure = f"Surat/Surat Mutasi/{year_now}/{month_now_roman}"

			# Create folders if not exist
			self.create_folders_if_not_exist("Home", folder_structure)

			# Final folder path after folder creation
			final_folder = f'Home/{folder_structure}'

			# Create the new file in the final folder
			_file = frappe.get_doc({
				"doctype": "File",
				"file_name": nama_surat,
				"folder": final_folder,
				"content": file_data,
				"is_private": 1,
				"ignore_duplicate_entry_error": True
			})
			_file.save()

			# Get the file URL (this is the public URL if the file is public, otherwise it's a private path)
			file_url = _file.file_url

			# Save the file URL or path back to the document
			self.doc_url = file_url  # Assumes 'file_url' field exists on the Surat Tugas doctype

			# Delete the temporary file
		except Exception as e:
			frappe.logger().error(f"Error uploading file: {e}")

		finally:
			if os.path.exists(file):
				os.remove(file)
				frappe.logger().info(f"Temporary file {file} deleted.")
				print(f"Temporary file {file} deleted.")
	

	def formatdate_indonesia_with_day(self, date_str):
		# Mengubah string tanggal menjadi objek tanggal
		date_obj = frappe.utils.getdate(date_str)

		# Membuat peta bulan dalam bahasa Indonesia
		bulan = [
			"", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
			"Juli", "Agustus", "September", "Oktober", "November", "Desember"
		]

		# Membuat peta hari dalam bahasa Indonesia
		hari = [
			"Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"
		]

		# Mendapatkan hari, tanggal, bulan, dan tahun
		hari_indonesia = hari[date_obj.weekday()]  # Mendapatkan nama hari
		tanggal = date_obj.day
		bulan_indonesia = bulan[date_obj.month]  # Mendapatkan nama bulan
		tahun = date_obj.year

		# Mengembalikan format: "Hari, DD Bulan YYYY"
		return f"{hari_indonesia}, {tanggal} {bulan_indonesia} {tahun}"

	def formatdate_indonesia(self, date_str):
		# Mengubah string tanggal menjadi objek tanggal
		date_obj = frappe.utils.getdate(date_str)

		# Membuat peta bulan dalam bahasa Indonesia
		bulan = [
			"", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
			"Juli", "Agustus", "September", "Oktober", "November", "Desember"
		]

		# Membuat peta hari dalam bahasa Indonesia
		hari = [
			"Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"
		]

		# Mendapatkan hari, tanggal, bulan, dan tahun
		tanggal = date_obj.day
		bulan_indonesia = bulan[date_obj.month]  # Mendapatkan nama bulan
		tahun = date_obj.year

		# Mengembalikan format: "Hari, DD Bulan YYYY"
		return f"{tanggal} {bulan_indonesia} {tahun}"

