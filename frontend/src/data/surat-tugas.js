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
			const suratTugas = await createDocumentResource({
				doctype: "Surat Tugas",
				name: suratTugasName,
			})

			// Update field langsung menggunakan setValue
			await suratTugas.setValue.submit({
				sudah_di_tanda_tangani: 1, // Centang tanda tangan
				ditanda_tangani_oleh: employeeName, // Isi nama penandatangan
			})

			alert("Surat tugas berhasil ditandatangani!")
		} else {
			alert("Anda belum menambahkan tanda tangan di profil.")
		}
	} catch (error) {
		console.log(error)
	}
}
