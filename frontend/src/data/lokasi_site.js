import router from "@/router"
import { createResource } from "frappe-ui"

export const getAllLokasiSite = createResource({
	url: "oims.api.get_all_lokasi_site",
	cache: "hrms:lokasi_site",
	onError(error) {
		if (error && error.exc_type === "AuthenticationError") {
			router.push({ name: "Login" })
		}
	},
})
