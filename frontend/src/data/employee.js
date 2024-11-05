import router from "@/router"
import { createResource } from "frappe-ui"

// export const employeeResource = {
// 	data: [],
// 	loading: false,
// 	error: null,
// 	async reload() {
// 	},
// }
export const employeeResource = createResource({
	url: "oims.api.get_current_employee_info",
	cache: "oims:employee",
	onError(error) {
		if (error && error.exc_type === "AuthenticationError") {
			router.push("/login")
		}
	},
})
