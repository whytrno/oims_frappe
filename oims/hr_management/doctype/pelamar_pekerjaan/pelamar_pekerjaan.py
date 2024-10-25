# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class PelamarPekerjaan(Document):
	pass

@frappe.whitelist()
def create_internal_applicant(doc_name,tanggal_interview_mulai,tanggal_interview_selesai):
	doc = frappe.get_doc("Pelamar Pekerjaan", doc_name)
	job = frappe.get_doc("Lowongan Pekerjaan", doc.judul_pekerjaan)
	event_subject = f'Interview {job.judul} - {doc.nama_pelamar}'

	frappe.get_doc({
		"doctype": "Event",
		"subject": event_subject,
		"starts_on": tanggal_interview_mulai,
		"ends_on": tanggal_interview_selesai,
		"event_type": "Private",
		"event_category": "Interview",
		"sync_with_google_calendar": 1,
		"add_video_conferencing": 1,
		"google_calendar": "Orecon Calendar",
		"event_participants": [
			{
				"reference_doctype": "Pelamar Pekerjaan",
				"reference_docname": doc.name,
			}
		]
	}).insert()
	frappe.msgprint("Internal Applicant Created")