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

		await isEmployeeAddSignature.fetch()

		// Jika karyawan sudah menambahkan tanda tangan
		if (isEmployeeAddSignature.data) {
			// Ambil resource dokumen Surat Tugas
			const suratTugas = createDocumentResource({
				doctype: "Surat Tugas",
				name: suratTugasName,
			})

			suratTugas.setValue.submit({
				sudah_di_tanda_tangani: 1, // Centang tanda tangan
				ditanda_tangani_oleh: employeeName, // Isi nama penandatangan
			})

			const signSuratTugas = createResource({
				url: "oims.api.sign_surat_tugas",
				params: {
					name: suratTugasName,
					employeeName: employeeName
				},
			})

			signSuratTugas.fetch()

			alert("Surat tugas berhasil ditandatangani!")
		} else {
			// alert("Anda belum menambahkan tanda tangan di profil.")
			const confirmation = confirm("Anda belum menambahkan tanda tangan di profil. Apakah Anda ingin menambahkan tanda tangan?")
			if(confirmation){
				// https://oims.orecon.co.id/perbaharui-data-karyawan/269
				window.location.href = `https://oims.orecon.co.id/perbaharui-data-karyawan/${employeeName}`
			}
		}
	} catch (error) {
		console.log(error)
	}
}
