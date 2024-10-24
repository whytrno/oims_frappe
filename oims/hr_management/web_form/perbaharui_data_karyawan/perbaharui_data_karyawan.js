frappe.ready(function () {
	// Dapatkan URL saat ini
	var currentUrl = window.location.pathname;

	// Split URL berdasarkan '/' dan ambil bagian setelah 'perbaharui-data-karyawan'
	var parts = currentUrl.split('/');
	var id = parts[2];

	// Dapatkan email user yang sedang login
	var currentUser = frappe.session.user;

	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Karyawan",
			filters: { "user_id": currentUser },
			fieldname: ["name", "alamat_ktp_sama_dengan_domisili"]
		},
		callback: function (response) {
			if (response.message) {
				var user_id = response.message.name;

				// Cek apakah email dari karyawan cocok dengan user yang sedang login
				if (id != user_id) {
					window.location.href = `/perbaharui-data-karyawan/${user_id}`;
				}

				if(response.message.alamat_ktp_sama_dengan_domisili) {
					$('div[data-fieldname="provinsi_ktp"]').parent().hide();
					$('div[data-label="Kabupaten KTP"]').parent().hide();
					$('div[data-label="Kecamatan KTP"]').parent().hide();
					$('div[data-label="Kelurahan KTP"]').parent().hide();
					$('div[data-label="Alamat KTP"]').parent().hide();
				}
			}
		}
	});

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
