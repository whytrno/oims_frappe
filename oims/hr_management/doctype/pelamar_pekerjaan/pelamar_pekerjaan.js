// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Pelamar Pekerjaan", {
	refresh: function (frm) {
		set_filters(frm);
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
