// Copyright (c) 2025, Wahyu Triono and contributors
// For license information, please see license.txt
frappe.ui.form.on('OIMS Notification', {
	validate: function (frm) {
		let count = 0;

		if (frm.doc.user) count++;
		if (frm.doc.jabatan) count++;
		if (frm.doc.semua_pengguna) count++;

		if (count === 0) {
			frappe.msgprint(__('Harap isi salah satu dari "User", "Jabatan", atau "Semua Pengguna".'));
			frappe.validated = false;
		} else if (count > 1) {
			frappe.msgprint(__('Hanya boleh mengisi salah satu dari "User", "Jabatan", atau "Semua Pengguna".'));
			frappe.validated = false;
		}
	}
});
