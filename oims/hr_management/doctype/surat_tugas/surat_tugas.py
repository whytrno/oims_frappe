# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import log
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm
import frappe
import os

class SuratTugas(Document):
	def before_save(self):
		try:
			karyawan_data = self.validate_karyawan_data()

			nama_surat_raw = f"{self.no_surat.replace('/', '_')} - {self.site}"
			nama_surat_temp = f"{nama_surat_raw}_temp.docx"
			nama_surat = f"{nama_surat_raw}.docx"
			penandatangan = frappe.get_doc('Karyawan', self.penanda_tangan)

			generated_docx = self.generate_document(nama_surat_temp, karyawan_data, penandatangan)
			self.upload_document_to_file_manager(nama_surat, generated_docx)
		except Exception as e:
			frappe.throw(e, title="Before Save Failed")
			raise

	def validate_karyawan_data(self):
		errors = []
		employee_ids = [row.employee_id for row in self.karyawan if row.employee_id]

		karyawan_data = frappe.get_all(
			"Karyawan",
			filters={"name": ["in", employee_ids]},
			fields=["name", "nama_lengkap", "nrp", "jabatan", "foto_ktp", "foto_vaksin", "status_kontrak"],
		)

		karyawan_map = {row["name"]: row for row in karyawan_data}
		tanggal_berangkat = self.formatdate_indonesia_with_day(self.tanggal_berangkat)

		for index, row in enumerate(self.karyawan, start=1):
			if row.employee_id and row.employee_id in karyawan_map:
				karyawan_doc = karyawan_map[row.employee_id]

				if not karyawan_doc["foto_ktp"]:
					errors.append(f"User {karyawan_doc['nama_lengkap']} belum upload foto KTP.")

				if karyawan_doc["status_kontrak"] == "Project Base":
					if not karyawan_doc["nrp"]:
						errors.append(f"User {karyawan_doc['nama_lengkap']} belum mengisi NRP.")

				if not karyawan_doc["jabatan"]:
					errors.append(f"User {karyawan_doc['nama_lengkap']} belum mengisi jabatan.")

				tanggal_pulang = "Menyesuaikan kebutuhan lapangan"
				if(row.tanggal_pulang):
					tanggal_pulang = self.formatdate_indonesia_with_day(row.tanggal_pulang)

				karyawan_doc['no'] = index
				karyawan_doc['tanggal_berangkat'] = tanggal_berangkat
				karyawan_doc['tanggal_pulang'] = tanggal_pulang
			else:
				errors.append(f"Data Karyawan dengan ID {row.employee_id} tidak ditemukan.")

		if errors:
			frappe.throw("<br>".join(errors), title="Validation Failed")

		return list(karyawan_map.values())

	def generate_document(self, nama_surat, karyawan, penandatangan):
		try:
			tanggal = frappe.utils.formatdate(frappe.utils.nowdate(), "dd MMMM yyyy")

			lokasi_site_doc = frappe.get_doc('Projek', self.site)
			lokasi_site_formatted = f'{lokasi_site_doc.nama_projek}'
			if lokasi_site_doc.lokasi_projek:
				lokasi_site_formatted += f', {lokasi_site_doc.lokasi_projek}'

			lokasi_site_formatted = lokasi_site_formatted.replace('&', '&amp;')
			tanggal_formatted = self.formatdate_indonesia(tanggal)

			if len(karyawan) > 1:
				template_path = frappe.get_app_path('oims', 'templates', 'docs', 'st_kelompok.docx')
				doc = DocxTemplate(template_path)
				return self.generate_kelompok_document(doc, karyawan, tanggal_formatted, nama_surat, lokasi_site_formatted, penandatangan)
			else:
				template_path = frappe.get_app_path('oims', 'templates', 'docs', 'st.docx')
				doc = DocxTemplate(template_path)

				return self.generate_single_document(doc, karyawan[0], tanggal_formatted, nama_surat, lokasi_site_formatted, penandatangan)

			# pdf_file_path = frappe.utils.get_site_path('private', 'files', 'surat_keterangan.pdf')
			# pypandoc.convert_file(docx_file_path, 'pdf', outputfile=pdf_file_path)
		except Exception as e:
			raise

	def generate_single_document(self, doc, karyawan, tanggal, nama_surat, lokasi_site_formatted, penandatangan):
		try:
			foto_ktp_path = None
			foto_vaksin_path = None
			if karyawan['foto_ktp'] is not None and karyawan['foto_ktp'] != '':
				foto_ktp_name = karyawan['foto_ktp'].split('/')[-1]
				foto_ktp_path = frappe.utils.get_site_path('private', 'files', foto_ktp_name)

			if karyawan['foto_vaksin'] is not None and karyawan['foto_vaksin'] != '':
				foto_vaksin_name = karyawan['foto_vaksin'].split('/')[-1]
				foto_vaksin_path = frappe.utils.get_site_path('private', 'files', foto_vaksin_name)

			context = {
				'nama_penandatangan': penandatangan.nama_lengkap,
				'jabatan_penandatangan': penandatangan.jabatan,
				'no_surat': self.no_surat,
				'keperluan': self.keperluan,
				'lokasi_site': lokasi_site_formatted,
				'tanggal': tanggal,
				'nama': karyawan['nama_lengkap'],
				'nrp': karyawan['nrp'],
				'jabatan': karyawan['jabatan'],
				'tanggal_berangkat': karyawan['tanggal_berangkat'],
				'tanggal_pulang': karyawan['tanggal_pulang'],
				'foto_ktp': InlineImage(doc, foto_ktp_path, width=Mm(80), height=Mm(50)) if foto_ktp_path else '',
				'foto_vaksin': InlineImage(doc, foto_ktp_path, width=Mm(80), height=Mm(50)) if foto_vaksin_path else '',
				'ttd': '{{ ttd }}'
			}

			doc.render(context)

			docx_file_path = frappe.utils.get_site_path('private', 'files', nama_surat)
			doc.save(docx_file_path)

			return docx_file_path
		except Exception as e:
			frappe.log_error("Error in generate_single_document", frappe.get_traceback(), "Surat Tugas")
			raise

	def generate_kelompok_document(self, doc, karyawan, tanggal, nama_surat, lokasi_site_formatted, penandatangan):
		try:
			table_context = []
			for row in karyawan:
				foto_ktp_path = None
				foto_ktp = ''
				foto_vaksin_path = None
				foto_vaksin = ''

				if row['foto_ktp'] is not None and row['foto_ktp'] != '':
					foto_ktp_name = row['foto_ktp'].split('/')[-1]
					foto_ktp_path = frappe.utils.get_site_path('private', 'files', foto_ktp_name)
					foto_ktp = InlineImage(doc, foto_ktp_path, width=Mm(80), height=Mm(50))

				if row['foto_vaksin'] is not None and row['foto_vaksin'] != '':
					foto_vaksin_name = row['foto_vaksin'].split('/')[-1]
					foto_vaksin_path = frappe.utils.get_site_path('private', 'files', foto_vaksin_name)
					foto_vaksin = InlineImage(doc, foto_vaksin_path, width=Mm(80), height=Mm(50))

				table_context.append({
					'no': row['no'],
					'nama': row['nama_lengkap'],
					'nrp': row['nrp'],
					'jabatan': row['jabatan'],
					'tanggal_berangkat': row['tanggal_berangkat'],
					'tanggal_pulang': row['tanggal_pulang'],
					'foto_ktp': foto_ktp,
					'foto_vaksin': foto_vaksin
				})


			table_context.reverse()

			context = {
				'nama_penandatangan': penandatangan.nama_lengkap,
				'jabatan_penandatangan': penandatangan.jabatan,
				'no_surat': self.no_surat,
				'keperluan': self.keperluan,
				'lokasi_site': lokasi_site_formatted,
				'tanggal': tanggal,
				'karyawan': table_context,
				'ttd': '{{ ttd }}'
			}

			doc.render(context)

			docx_file_path = frappe.utils.get_site_path('private', 'files', nama_surat)
			doc.save(docx_file_path)

			return docx_file_path
		except Exception as e:
			frappe.log_error("Error in generate_kelompok_document", f'{e} \n\n {frappe.get_traceback()}', "Surat Tugas")
			raise

	def create_folders_if_not_exist(self, base_path, folder_path):
		try:
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
						# "is_private": 1
					})
					folder_doc.save()
					frappe.logger().info(f"Folder '{folder}' created in '{current_folder}'")
		except Exception as e:
			frappe.log_error("Error in create_folders_if_not_exist", frappe.get_traceback(), "Surat Tugas")
			raise

	def upload_document_to_file_manager(self, nama_surat, file):
		try:
			with open(file, 'rb') as f:
				file_data = f.read()

			# Get the current year and month in Roman numeral format
			year_now = frappe.utils.nowdate().split('-')[0]
			month_now_roman = frappe.utils.formatdate(frappe.utils.nowdate(), "MM")

			# Define the full folder path based on your structure
			folder_structure = f"Surat/Surat Tugas/{year_now}/{month_now_roman}"

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
				# "is_private": 1,
				"ignore_duplicate_entry_error": True
			})
			_file.save()

			# Get the file URL (this is the public URL if the file is public, otherwise it's a private path)
			file_url = _file.file_url

			# Save the file URL or path back to the document
			self.doc_url = file_url
		except Exception as e:
			frappe.log_error("Error in upload_document_to_file_manager", frappe.get_traceback(), "Surat Tugas")
			raise
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
