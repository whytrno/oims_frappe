// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Karyawan", {
	refresh: function (frm) {
		set_filters(frm);
	},
	provinsi_domisili: function (frm) {
		clear_fields_on_change(frm, 'kabupaten_domisili', 'kecamatan_domisili');
		set_filters(frm, 'Provinsi', 'provinsi_domisili', 'kabupaten_domisili', 'province_id');
	},
	kabupaten_domisili: function (frm) {
		clear_fields_on_change(frm, 'kecamatan_domisili');
		set_filters(frm, 'Kabupaten', 'kabupaten_domisili', 'kecamatan_domisili', 'regency_id');
	},
	kecamatan_domisili: function (frm) {
		clear_fields_on_change(frm, 'kelurahan_domisili');
		clear_fields_on_change(frm, 'alamat_domisili');
	},

	provinsi_ktp: function (frm) {
		clear_fields_on_change(frm, 'kabupaten_ktp', 'kecamatan_ktp');
		set_filters(frm, 'Provinsi', 'provinsi_ktp', 'kabupaten_ktp', 'province_id');
	},
	kabupaten_ktp: function (frm) {
		clear_fields_on_change(frm, 'kecamatan_ktp');
		set_filters(frm, 'Kabupaten', 'kabupaten_ktp', 'kecamatan_ktp', 'regency_id');
	},
	kecamatan_ktp: function (frm) {
		clear_fields_on_change(frm, 'kelurahan_ktp');
		clear_fields_on_change(frm, 'alamat_ktp');
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
	// Loop through all fields passed as arguments and clear their values if they are filled
	fields.forEach(field => {
		if (frm.doc[field]) {
			frm.set_value(field, null);  // Set field value to null (clears the field)
		}
	});
}
