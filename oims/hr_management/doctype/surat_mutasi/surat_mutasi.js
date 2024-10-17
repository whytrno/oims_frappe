// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Surat Mutasi", {
    refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button('Download Surat', () => {
				const file_name_raw = frm.doc.doc_url;
				const file_name = file_name_raw.split("/").pop();

				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "File",
						filters: {
							"file_name": ['like', file_name]
						},
						fields: ["name", "file_url"],
						limit_page_length: 1
					},
					callback: function (r) {
						if (r.message && r.message.length > 0) {
							let file_url = r.message[0].file_url;
							console.log("file_url", file_url);
							window.open(file_url, '_blank');
						} else {
							frappe.msgprint(__('File not found!'));
						}
					}
				});
			});
		}
	},

	onload: function (frm) {
		if (frm.is_new()) {
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Surat Mutasi",
					fields: ["surat_ke"],
					limit_page_length: 1,
					order_by: "creation desc"
				},
				callback: function (r) {
					if (r.message && r.message.length > 0) {
						let last_no_surat = r.message[0].surat_ke;
						frm.set_value('surat_ke', last_no_surat + 1);
					} else {
						frm.set_value('surat_ke', 1);
					}
				}
			});
		}
	},

    surat_ke: function (frm) {
		if (frm.doc.surat_ke) {
			surat_ke = frm.doc.surat_ke
			site = frm.doc.site
			frm.set_value('no_surat', generate_no_surat(surat_ke, site));
		}
	},

    karyawan: function (frm) {
        if (frm.doc.karyawan) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Karyawan",
                    name: frm.doc.karyawan
                },
                callback: function (r) {
                    if (r.message) {
                        frm.set_value('dari_divisi', r.message.divisi);
                        frm.set_value('ke_divisi', r.message.divisi);
                        frm.set_value('ke_jabatan', r.message.jabatan);
                    }
                }
            });
        }
    }
});

function generate_no_surat(surat_ke){
	let current_date = new Date();
	let month_roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][current_date.getMonth()];
	let year = current_date.getFullYear();

    let no_surat = `8E/${surat_ke}/MT/HO/OSP/${month_roman}/${year}`;

	return no_surat
}