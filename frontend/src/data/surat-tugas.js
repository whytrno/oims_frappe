import { createResource } from "frappe-ui"

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
