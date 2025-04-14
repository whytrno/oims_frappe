frappe.ready(function () {
	$(document).on("change", "input[data-fieldname='alamat_ktp_sama_dengan_domisili']", function() {
		if ($(this).prop('checked')) {
			$('div[data-fieldname="provinsi_ktp"]').parent().hide();
			$('div[data-label="Kabupaten KTP"]').parent().hide();
			$('div[data-label="Kecamatan KTP"]').parent().hide();
			$('div[data-label="Kelurahan KTP"]').parent().hide();
			$('div[data-label="Alamat KTP"]').parent().hide();
		} else {
			$('div[data-fieldname="provinsi_ktp"]').parent().show();
			$('div[data-label="Kabupaten KTP"]').parent().show();
			$('div[data-label="Kecamatan KTP"]').parent().show();
			$('div[data-label="Kelurahan KTP"]').parent().show();
			$('div[data-label="Alamat KTP"]').parent().show();
		}
	});

});
