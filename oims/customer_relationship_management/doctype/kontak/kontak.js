// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Kontak", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button('Lihat Perusahaan', () => {
                frappe.set_route("Form", "Perusahaan", frm.doc.perusahaan);
            });
        }
	},
});
