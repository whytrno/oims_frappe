import { createResource } from "frappe-ui"

export const hazardReportsResource = createResource({
    url: "oims.api.get_all_hazard_report",
    cache: "oims:hazard_reports",
})