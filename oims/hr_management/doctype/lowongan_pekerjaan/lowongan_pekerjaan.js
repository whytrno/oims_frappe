// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lowongan Pekerjaan", {
	refresh: function (frm) {
		set_filters(frm);
	},
	provinsi_penempatan: function (frm) {
		clear_fields_on_change(frm, 'kabupaten_penempatan', 'kecamatan_domisili');
		set_filters(frm, 'Provinsi', 'provinsi_penempatan', 'kabupaten_penempatan', 'province_id');
	},
	kabupaten_penempatan: function (frm) {
		set_filters(frm, 'Kabupaten', 'kabupaten_penempatan', 'kecamatan_domisili', 'regency_id');
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
