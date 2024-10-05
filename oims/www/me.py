# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: MIT. See LICENSE

import frappe
import frappe.www.list
from frappe import _

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.throw(_("You need to be logged in to access this page"), frappe.PermissionError)

	context.current_user = frappe.get_doc("User", frappe.session.user)
	current_employee = None

	try:
		current_employee = frappe.get_doc("Karyawan", {"user_id": frappe.session.user})
	except frappe.DoesNotExistError:
		pass

	context.current_employee = current_employee

	context.show_sidebar = True
