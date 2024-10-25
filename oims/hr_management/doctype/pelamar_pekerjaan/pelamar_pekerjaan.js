// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pelamar Pekerjaan", {
	refresh: function (frm) {
		set_filters(frm);

        if (!frm.is_new()) {
			frm.add_custom_button(__("Interview"), () => {
				const nama_pelamar = frm.doc.nama_pelamar;
				const name = frm.doc.name;
				frappe.prompt(
				[ 
					{
						'fieldname': 'name', 
						'fieldtype': 'Data', 
						'label': 'Name', 
						'reqd': 1,
						"read_only": 1,
						'default': name
					},
					{
						'fieldname': 'nama_pelamar', 
						'fieldtype': 'Data', 
						'label': 'Nama Pelamar', 
						'reqd': 1,
						"read_only": 1,
						'default': nama_pelamar
					},
					{
						'fieldname': 'tanggal_interview_mulai', 
						'fieldtype': 'Datetime', 
						'label': 'Tanggal Interview Mulai', 
						'reqd': 1
					},
					{
						'fieldname': 'tanggal_interview_selesai', 
						'fieldtype': 'Datetime', 
						'label': 'Tanggal Interview Selesai', 
						'reqd': 1
					} 
				], 
				function(values){ 
					frappe.call({
						method: 'oims.hr_management.doctype.pelamar_pekerjaan.pelamar_pekerjaan.create_internal_applicant',
						args: {
							'doc_name': values.name,
							'tanggal_interview_mulai': values.tanggal_interview_mulai,
							'tanggal_interview_selesai': values.tanggal_interview_selesai
						},
						callback: function(r) {
							if(r.message) {
								frappe.msgprint("Internal Applicant Created");
							}
						}
					});
				}, 'Pembuat Jadwal Interview', 'Submit' )
			}, __("Chat Whatsapp"));
			
            // frm.add_custom_button('Interview', () => {
			// 	var phone = frm.doc.no_hp;
			// 	phone = phone.replace(/-/g, '');
			// 	const pelamar = frm.doc.nama_pelamar;
			// 	const message = `Halo ${pelamar}, saya HRD dari PT ORECON SADANUS PERKASA, ingin mengundang saudara untuk interview pada...`;
			// 	const url = `https://wa.me/${phone}?text=${message}`;
			// 	window.open(url, '_blank');
            // }, __("Chat Whatsapp"));

            frm.add_custom_button('Offering letter', () => {
				var phone = frm.doc.no_hp;
				phone = phone.replace(/-/g, '');
				const pelamar = frm.doc.nama_pelamar;
				const message = `Halo ${pelamar}, saya HRD dari PT ORECON SADANUS PERKASA, ingin menawarkan offering letter...`;
				const url = `https://wa.me/${phone}?text=${message}`;
				window.open(url, '_blank');
            }, __("Chat Whatsapp"));

            frm.add_custom_button('Tolak', () => {
				var phone = frm.doc.no_hp;
				phone = phone.replace(/-/g, '');
				const pelamar = frm.doc.nama_pelamar;
				const message = `Halo ${pelamar}, saya HRD dari PT ORECON SADANUS PERKASA, ingin menginformasikan bahwa saudara di tolak...`;
				const url = `https://wa.me/${phone}?text=${message}`;
				window.open(url, '_blank');
            }, __("Chat Whatsapp"));
        }
	},
	provinsi_domisili: function (frm) {
		clear_fields_on_change(frm, 'kabupaten_domisili', 'kecamatan_domisili');
		set_filters(frm, 'Provinsi', 'provinsi_domisili', 'kabupaten_domisili', 'province_id');
	},
	kabupaten_domisili: function (frm) {
		set_filters(frm, 'Kabupaten', 'kabupaten_domisili', 'kecamatan_domisili', 'regency_id');
	},

	
});

function set_filters(frm, doctype, field_awal, field_tujuan, filter) {
	if (frm.doc[field_awal]) {
		frappe.db.get_value(doctype, { 'nama': frm.doc[field_awal] }, 'id', (r) => {
			if (r && r.id) {
				frm.set_query(field_tujuan, function () {
					return {
						filters: {
							[filter]: r.id
						}
					};
				});
				frm.refresh_field(field_tujuan);
			}
		});
	} else {
		frm.set_query(field_tujuan, function () {
			return {};
		});
	}
}

function clear_fields_on_change(frm, ...fields) {
	fields.forEach(field => {
		if (frm.doc[field]) {
			frm.set_value(field, null);
		}
	});
}
