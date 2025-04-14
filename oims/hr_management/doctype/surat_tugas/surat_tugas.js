// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Surat Tugas", {
    before_save: async function (frm) {
		// console.log(frm.doc.karyawan_surat_tugas)
        // let karyawan_nama_list = frm.doc.karyawan_surat_tugas.map(row => row.nama_karyawan);
        // frm.set_value('karyawan_for_list_view', karyawan_nama_list.join(', '));
		// console.log("karyawan_nama_list", karyawan_nama_list);

		validate_site(frm)
    },

	onload: function (frm) {
		if (frm.is_new()) {
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
		}

		frappe.db.get_value('Karyawan', {'nrp': '8019002'}, 'name')
			.then(r => {
				if (r.message) {
					frm.set_value('penanda_tangan', r.message.name);
				}
			});

		// Tetap set query untuk user_email baik saat create maupun update
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
			// frm.add_custom_button('Lihat Surat', () => {
			// 	const file_name_raw = frm.doc.file_url;
			// 	const file_name = file_name_raw.split("/").pop();

			// 	frappe.call({
			// 		method: "frappe.client.get_list",
			// 		args: {
			// 			doctype: "File",
			// 			filters: {
			// 				"file_name": ['like', file_name]
			// 			},
			// 			fields: ["name", "file_name"],
			// 			limit_page_length: 1
			// 		},
			// 		callback: function (r) {
			// 			console.log("r", r);
			// 			if (r.message && r.message.length > 0) {
			// 				let file_id = r.message[0].name;
			// 				console.log("file_id", file_id);

			// 				const route = `/app/file/${file_id}`;
			// 				window.open(route, '_blank');
			// 			} else {
			// 				frappe.msgprint(__('File not found!'));
			// 			}
			// 		}
			// 	});
			// });
			frm.add_custom_button('Download Surat', () => {
				// const file_name_raw = frm.doc.doc_url;
				// const file_name = file_name_raw.split("/").pop();

				const doc_name_raw = frm.doc.name
				const site = frm.doc.site
				const doc_name_final = doc_name_raw.replace(/\//g, '_');
				const doc_url = `${doc_name_final} - ${site}.docx`

				frappe.call({
					method: "frappe.client.get_list",
					args: {
						doctype: "File",
						filters: {
							"file_name": ['like', doc_url]
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
	},

	surat_ke: function (frm) {
		if (frm.doc.surat_ke) {
			surat_ke = frm.doc.surat_ke
			site = frm.doc.site
			frm.set_value('no_surat', generate_no_surat(surat_ke, site));
		}
	},

	site: function (frm) {
        if (frm.doc.site) {
            validate_site(frm);
        }
    },
});

function generate_no_surat(surat_ke){
	let current_date = new Date();
	let month_roman = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII'][current_date.getMonth()];
	let year = current_date.getFullYear();

	let no_surat = `15/${surat_ke}/ST/OSP/${month_roman}/${year}`;

	return no_surat
}

function validate_site(frm, throw_error = false) {
    frappe.call({
        method: "frappe.client.get",
        args: {
            doctype: "Projek",
            name: frm.doc.site  // Menggunakan field `site` untuk mengambil data projek
        },
        callback: function (r) {
            if (r.message) {
                let projek = r.message;

                let errors = [];
                if (!projek.nama_projek) {
                    errors.push(`Nama Projek belum diisi pada Projek ${frm.doc.site}.`);
                }
                if (!projek.lokasi_projek) {
                    errors.push(`Lokasi Projek belum diisi pada Projek ${frm.doc.site}.`);
                }

                // Jika ada kesalahan, tampilkan pesan error
                if (errors.length > 0) {
                    frappe.msgprint({
                        title: __('Error'),
                        indicator: 'red',
                        message: errors.join('<br>')
                    });

                    // Jika validasi dilakukan saat save, maka hentikan penyimpanan
                    if (throw_error) {
                        frappe.validated = false;
                    }
                }
            }
        }
    });
}

frappe.ui.form.on('Karyawan Surat Tugas', {
	employee_id: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		check_if_ktp_uploaded(frm, row.employee_id);
		set_karyawan_to_karyawan_for_list_view(frm, row.nama_karyawan);
	},
});

function set_karyawan_to_karyawan_for_list_view(frm, nama_karyawan) {
	let karyawan_list = frm.doc.karyawan_for_list_view ? frm.doc.karyawan_for_list_view.split(', ') : [];

	if (!karyawan_list.includes(nama_karyawan)) {  // Hindari duplikasi
		karyawan_list.push(nama_karyawan);
	}

	frm.set_value('karyawan_for_list_view', karyawan_list.join(', '));
}

function check_if_ktp_uploaded(frm, name) {
	frappe.call({
		method: "frappe.client.get",
		args: {
			doctype: "Karyawan",
			filters: {
				"name": name
			}
		},
		callback: function (r) {
			if (r.message) {
				let errors = [];

				if (!r.message.foto_ktp) {
					errors.push(`Karyawan dengan ID: ${name} belum upload foto KTP.`);
				}

				if (!r.message.jabatan) {
					errors.push(`Karyawan dengan ID: ${name} belum mengisi jabatan.`);
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
