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
		const isEmployeeAddSignature = await createResource({
			url: "oims.api.is_employee_add_signature",
			params: { name: employeeName },
			cache: `oims:is_employee_add_signature:${employeeName}`,
		})

		await isEmployeeAddSignature.fetch()

		if (isEmployeeAddSignature.data) {
			const signSuratTugas = await createResource({
				url: "oims.api.sign_surat_tugas",
				params: {
					name: suratTugasName,
					employeeName: employeeName
				},
			})

			await signSuratTugas.fetch()

			suratTugas.reload()
			alert("Surat tugas berhasil ditandatangani!")
		} else {
			const confirmation = confirm("Anda belum menambahkan tanda tangan di profil. Apakah Anda ingin menambahkan tanda tangan?")
			if (confirmation) {
				window.location.href = `https://oims.orecon.co.id/perbaharui-data-karyawan/${employeeName}`
			}
		}

	} catch (error) {
		console.log(error)
	}
}
