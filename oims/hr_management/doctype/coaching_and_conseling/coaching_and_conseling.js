// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Coaching and Conseling", {
	refresh(frm) {

	},
    onload(frm) {
        if(frappe.session.user !== "Administrator") {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Karyawan",
                    filters: {
                        "user_id": frappe.session.user_email
                    }
                },
                callback: function (r) {
                    if (r.message) {
                        let karyawan = r.message;
                        frm.set_value("pemberi_konseling", karyawan.nrp);
                    }
                }
            });
        }else{
            frm.set_df_property("pemberi_konseling", "read_only", 0);
        }
    }
});
