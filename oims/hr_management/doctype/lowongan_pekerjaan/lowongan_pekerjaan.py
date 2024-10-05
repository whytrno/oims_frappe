# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import pretty_date
from frappe.website.website_generator import WebsiteGenerator
from frappe import _

class LowonganPekerjaan(WebsiteGenerator):
	website = frappe._dict(
		template="templates/generators/job_opening.html",
		condition_field="publish",
		page_title_field="judul",
	)
	def get_context(self, context):
		context.judul = self.judul
		context.deskripsi = self.deskripsi
		context.perusahaan = self.perusahaan
		context.divisi = self.divisi
		context.dibuka_pada = pretty_date(self.dibuka_pada)
		context.ditutup_pada = self.ditutup_pada
		context.jenis_kontrak = self.jenis_kontrak
		context.lokasi = self.lokasi
		context.gaji_minimal = self.gaji_minimal
		context.gaji_maksimal = self.gaji_maksimal
		context.dibayarkan_setiap = self.dibayarkan_setiap
