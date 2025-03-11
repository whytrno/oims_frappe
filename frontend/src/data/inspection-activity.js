import { createResource } from "frappe-ui"

export const inspectionActivityResource = createResource({
	url: "oims.api.get_all_inspection_activities",
	cache: "oims:inspection_activities",
})
