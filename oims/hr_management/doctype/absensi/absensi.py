# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Absensi(Document):
	def autoname(self):
		karyawan = frappe.get_doc("Karyawan", self.karyawan)

		if karyawan:
			self.name = karyawan.nama_lengkap + " - " + self.waktu_absen
		else:
			frappe.throw("Karyawan tidak ditemukan untuk NRP tersebut")
