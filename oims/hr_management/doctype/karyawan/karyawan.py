# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Karyawan(Document):
    def before_insert(self):
        '''
		Membuat User baru dengan data yang sama
  		'''
        if not self.email:
            self.make_email_from_name()
        user = frappe.get_doc({
			"doctype": "User",
			"email": self.email,
			"first_name": self.nama_lengkap,
			"send_welcome_email": 0,
			"new_password": "orecongroup123",
			# "module_profile": "Karyawan",
			"roles": [{
				"role": "Karyawan"
			}],
		})

        user.insert(ignore_permissions=True)
        frappe.db.commit()

        self.beri_akses_untuk_login_oims_app = 1
        self.user_id = user.name

    def before_save(self):
        if self.alamat_ktp_sama_dengan_domisili:
            self.provinsi_ktp = self.provinsi_domisili
            self.kabupaten_ktp = self.kabupaten_domisili
            self.kecamatan_ktp = self.kecamatan_domisili
            self.kelurahan_ktp = self.kelurahan_domisili
            self.alamat_ktp = self.alamat_domisili


    def make_email_from_name(self):
        '''
		Membuat email dari nama lengkap
		'''
        if self.nama_lengkap:
        	self.email = self.nama_lengkap.replace(" ", "").lower() + "@orecon.co.id"
