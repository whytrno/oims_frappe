import router from "@/router"
import { createResource } from "frappe-ui"

export const unitDetail = createResource(unit, {
	url: "minning_production.api.get_unit_info",
	params: {
		unit_id: unit,
	},
	onError(error) {
		if (error && error.exc_type === "AuthenticationError") {
			router.push("/login")
		}
	},
})
