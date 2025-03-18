import { createDocumentResource, createResource } from "frappe-ui"

export const getAllSuratTugas = createResource({
	url: "oims.api.get_all_surat_tugas",
	cache: "oims:surat_tugas",
})

export const getSuratTugasDetail = (name) =>
	createResource({
		url: "oims.api.get_surat_tugas_detail",
		params: { name },
		cache: `oims:surat_tugas_detail:${name}`,
	})

export const getSuratTugasDocUrl = (name) =>
	createResource({
		url: "oims.api.get_surat_tugas_doc_file",
		params: { name },
		cache: `oims:surat_tugas_doc_file:${name}`,
	})

export const tandaTanganiSuratTugas = async (employeeName, suratTugasName) => {
	try {
		// Cek apakah karyawan sudah menambahkan tanda tangan
		const isEmployeeAddSignature = await createResource({
			url: "oims.api.is_employee_add_signature",
			params: { name: employeeName },
			cache: `oims:is_employee_add_signature:${employeeName}`,
		})

		console.log("Mulai proses tanda tangan...")

		// Cek tanda tangan karyawan
		console.log("Memeriksa apakah karyawan sudah menambahkan tanda tangan...")
		await isEmployeeAddSignature.fetch()
		console.log("Hasil pengecekan:", isEmployeeAddSignature.data)

		if (isEmployeeAddSignature.data) {
			console.log("Karyawan sudah memiliki tanda tangan. Melanjutkan proses tanda tangan...")

			// const suratTugas = await createDocumentResource({
			// 	doctype: "Surat Tugas",
			// 	name: suratTugasName,
			// })

			console.log("Dokumen Surat Tugas berhasil diambil:", suratTugas)

			console.log("Data Surat Tugas diperbarui, melakukan submit...")
			// await suratTugas.setValue.submit({
			// 	sudah_di_tanda_tangani: 1,
			// 	ditanda_tangani_oleh: employeeName,
			// })

			console.log("Surat Tugas berhasil disubmit.")

			// Panggil API untuk update status di server
			const signSuratTugas = await createResource({
				url: "oims.api.sign_surat_tugas",
				params: {
					name: suratTugasName,
					employeeName: employeeName
				},
			})

			console.log("Memanggil API sign_surat_tugas...")
			await signSuratTugas.fetch()
			console.log("API sign_surat_tugas berhasil dipanggil.")

			suratTugas.reload()
			alert("Surat tugas berhasil ditandatangani!")
		} else {
			console.log("Karyawan belum memiliki tanda tangan.")
			const confirmation = confirm("Anda belum menambahkan tanda tangan di profil. Apakah Anda ingin menambahkan tanda tangan?")
			if (confirmation) {
				window.location.href = `https://oims.orecon.co.id/perbaharui-data-karyawan/${employeeName}`
			}
		}

	} catch (error) {
		console.log(error)
	}
}
