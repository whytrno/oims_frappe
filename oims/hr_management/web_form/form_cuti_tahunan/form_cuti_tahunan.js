frappe.ready(function () {
	var currentUser = frappe.session.user;

	if (frappe.web_form.is_new) {
		frappe.web_form.set_df_property("ttd_penerima_job_pending", "hidden", 1);
	} else {
		setTimeout(() => {
			$(`input[data-fieldname="karyawan_penerima_job_pending"]`).attr("readonly", true);
		}, 300);
	}

	frappe.call({
		method: "frappe.client.get_value",
		args: {
			doctype: "Karyawan",
			filters: { "user_id": currentUser },
			fieldname: ["name"]
		},
		callback: function (response) {
			if (response.message?.name) {
				const currentKaryawan = response.message.name;

				if (!frappe.web_form.get_value("karyawan_pemohon")) {
					frappe.web_form.set_value("karyawan_pemohon", currentKaryawan);
				}

				setTimeout(() => {
					$(`input[data-fieldname="karyawan_pemohon"]`).attr("readonly", true);
				}, 300);

				const pemohon = frappe.web_form.get_value("karyawan_pemohon");
				const penerima = frappe.web_form.get_value("karyawan_penerima_job_pending");

				if (currentKaryawan == pemohon) {
					frappe.web_form.set_df_property("ttd_penerima_job_pending", "read_only", 1);
				} else if (currentKaryawan == penerima) {
					frappe.web_form.fields.forEach(field => {
						if (!["ttd_penerima_job_pending", "karyawan_pemohon", "karyawan_penerima_job_pending"].includes(field.fieldname)) {
							frappe.web_form.set_df_property("ttd_pemohon", "read_only", 1);
							frappe.web_form.set_df_property("tanggal_mulai_cuti", "read_only", 1);
							frappe.web_form.set_df_property("tanggal_selesai_cuti", "read_only", 1);
							frappe.web_form.set_df_property(field.fieldname, "read_only", 1);
						} else {
							frappe.web_form.set_df_property("ttd_penerima_job_pending", "read_only", 0);
							frappe.web_form.set_df_property("ttd_penerima_job_pending", "hidden", 0);
						}
					});
				}
			}
		}
	});

	// Hitung selama_hari
	frappe.web_form.on('tanggal_mulai_cuti', () => hitungSelamaHari());

	frappe.web_form.on('tanggal_selesai_cuti', () => {
		const tanggalMulai = frappe.web_form.get_value("tanggal_mulai_cuti");
		const tanggalSelesai = frappe.web_form.get_value("tanggal_selesai_cuti");

		if (tanggalMulai && tanggalSelesai) {
			const mulai = new Date(tanggalMulai);
			const selesai = new Date(tanggalSelesai);

			if (selesai < mulai) {
				frappe.msgprint("Tanggal selesai cuti tidak boleh lebih awal dari tanggal mulai cuti.");
				frappe.web_form.set_value("tanggal_selesai_cuti", "");
				frappe.web_form.set_value("selama_hari", "");
				return;
			}
		}

		hitungSelamaHari();
	});
});

function hitungSelamaHari() {
	const tanggalMulai = frappe.web_form.get_value("tanggal_mulai_cuti");
	const tanggalSelesai = frappe.web_form.get_value("tanggal_selesai_cuti");

	if (tanggalMulai && tanggalSelesai) {
		const mulai = new Date(tanggalMulai);
		const selesai = new Date(tanggalSelesai);

		const gapHari = Math.floor((selesai - mulai) / (1000 * 60 * 60 * 24)) + 1;

		frappe.web_form.set_value("selama_hari", gapHari > 0 ? gapHari : 0);
	}
}
