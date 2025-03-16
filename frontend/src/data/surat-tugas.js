import { createResource } from "frappe-ui"

export const getAllSuratTugas = createResource({
	url: "oims.api.get_all_surat_tugas",
	cache: "oims:surat_tugas",
})

export const getSuratTugasDetail = createResource({
	url: "oims.api.get_all_surat_tugas",
	cache: "oims:surat_tugas",
})
