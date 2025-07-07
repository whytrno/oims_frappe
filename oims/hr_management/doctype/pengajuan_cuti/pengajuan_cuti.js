// Copyright (c) 2025, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pengajuan Cuti", {
	refresh: function (frm) {
		if (!frm.is_new()) {
			if (frm.doc.doc_url) {
				frm.add_custom_button('Download Surat', () => {
					let doc_name = frm.doc.doc_url || "";

					if (doc_name.startsWith("/files/")) {
						doc_name = doc_name.replace("/files/", "");
					}

					frappe.call({
						method: "frappe.client.get_list",
						args: {
							doctype: "File",
							filters: {
								"file_name": ['like', doc_name]
							},
							fields: ["name", "file_url"],
							limit_page_length: 1
						},
						callback: function (r) {
							if (r.message && r.message.length > 0) {
								let file_url = r.message[0].file_url;
								window.open(file_url, '_blank');
							} else {
								frappe.msgprint(__('File not found!'));
							}
						}
					});
				});
			}
		}
	},
});
