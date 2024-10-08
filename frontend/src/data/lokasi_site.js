import router from "@/router"
import { createResource } from "frappe-ui"

export const getAllLokasiAbsen = createResource({
	url: "oims.api.get_all_lokasi_absen",
	cache: "hrms:lokasi_absen",
	onError(error) {
		if (error && error.exc_type === "AuthenticationError") {
			router.push({ name: "Login" })
		}
	},
})
