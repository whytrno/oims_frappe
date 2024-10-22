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
			fieldname: "name"
		},
		callback: function (response) {
			if (response.message) {
				var user_id = response.message.name;

				// Cek apakah email dari karyawan cocok dengan user yang sedang login
				if (id != user_id) {
					window.location.href = `/perbaharui-data-karyawan/${user_id}`;
				}
			}
		}
	});
});
