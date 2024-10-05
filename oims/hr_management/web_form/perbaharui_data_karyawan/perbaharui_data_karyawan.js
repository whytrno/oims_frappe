frappe.ready(function () {
	// Dapatkan URL saat ini
	var currentUrl = window.location.pathname;

	// Split URL berdasarkan '/' dan ambil bagian setelah 'perbaharui-data-karyawan'
	var parts = currentUrl.split('/');
	var nrp = parts[2];  // Ini adalah NRP dari URL
	console.log(nrp)

	// Dapatkan email user yang sedang login
	var currentUser = frappe.session.user;

	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Karyawan",
			filters: { "user_id": currentUser },
			fieldname: "nrp"
		},
		callback: function (response) {
			console.log(response)
			if (response.message) {
				var user_nrp = response.message.nrp;

				// Cek apakah email dari karyawan cocok dengan user yang sedang login
				if (nrp !== user_nrp) {
					window.location.href = `/perbaharui-data-karyawan/${user_nrp}`;
				}
			}
		}
	});
});
