// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Surat Tugas", {
	onload: function (frm) {
		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Surat Tugas",
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
		frm.fields_dict['karyawan'].grid.get_field('user_email').get_query = function (doc, cdt, cdn) {
			return {
				filters: {
					'ignore_user_type': 1
				}
			};
		};
	},

	refresh: function (frm) {
		if (!frm.is_new()) {
			frm.add_custom_button('Lihat Surat', () => {
				const file_name_raw = frm.doc.file_url;
				const file_name = file_name_raw.split("/").pop();

				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "File",
						filters: {
							"file_name": ['like', file_name]
						},
						fields: ["name", "file_name"],
						limit_page_length: 1
					},
					callback: function (r) {
						console.log("r", r);
						if (r.message && r.message.length > 0) {
							let file_id = r.message[0].name;
							console.log("file_id", file_id);

							const route = `/app/file/${file_id}`;
							window.open(route, '_blank');
						} else {
							frappe.msgprint(__('File not found!'));
						}
					}
				});
			});
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

	surat_ke: function (frm) {
		if (frm.doc.surat_ke) {
			let surat_ke = frm.doc.surat_ke;
			let current_date = new Date();
			let month_roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][current_date.getMonth()];
			let year = current_date.getFullYear();

			let no_surat = `15-${surat_ke}-ST-OSP-${month_roman}-${year}`;

			frm.set_value('no_surat', no_surat);
		}
	},
});

frappe.ui.form.on('Karyawan Surat Tugas', {
	nrp: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		check_if_ktp_uploaded(frm, row.nama_karyawan);
	}
});

function check_if_ktp_uploaded(frm, karyawan_nama_karyawan) {
	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Karyawan",
			filters: {
				"nama_lengkap": karyawan_nama_karyawan
			}
		},
		callback: function (r) {
			if (r.message) {
				let errors = [];

				if (!r.message.foto_ktp) {
					errors.push(`User ${karyawan_nama_karyawan} belum upload foto KTP.`);
				}

				if (!r.message.jabatan) {
					errors.push(`User ${karyawan_nama_karyawan} belum mengisi jabatan.`);
				}

				if (errors.length > 0) {
					frappe.msgprint({
						title: __('Error'),
						indicator: 'red',
						message: errors.join('<br>')
					});
				}
			}
		}
	});
}
