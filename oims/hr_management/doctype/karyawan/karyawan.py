# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Karyawan(Document):
	def before_save(self):
		if self.alamat_ktp_sama_dengan_domisili:
			self.provinsi_ktp = self.provinsi_domisili
			self.kabupaten_ktp = self.kabupaten_domisili
			self.kecamatan_ktp = self.kecamatan_domisili
			self.kelurahan_ktp = self.kelurahan_domisili
			self.alamat_ktp = self.alamat_domisili