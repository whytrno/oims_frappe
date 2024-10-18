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

    def before_save(self):
        lokasi_absen = frappe.get_doc("Lokasi Absen", self.lokasi_absen)
        waktu_absen = ""
        
        if self.tipe == "In":
            waktu_absen = frappe.utils.get_time(lokasi_absen.waktu_masuk)
        elif self.tipe == "Out":
            waktu_absen = frappe.utils.get_time(lokasi_absen.waktu_keluar)

        waktu_sekarang = frappe.utils.get_time(self.waktu_absen)
        
        if waktu_sekarang > waktu_absen:
            self.telat = 1
