import { createResource, createListResource } from "frappe-ui"
import { userResource } from "./user"

export const unreadNotificationsCount = {
	data: [],
	loading: false,
	error: null,
	async reload() {
	},
}
// export const unreadNotificationsCount = createResource({
// 	url: "oims.api.get_unread_notifications_count",
// 	cache: "oims:unread_notifications_count",
// 	initialData: 0,
// 	auto: true,
// })

export const notifications = {
	data: [],
	loading: false,
	error: null,
	async reload() {
	},
}
// export const notifications = createListResource({
// 	doctype: "PWA Notification",
// 	filters: { to_user: userResource.data.name },
// 	fields: [
// 		"name",
// 		"from_user",
// 		"message",
// 		"read",
// 		"creation",
// 		"reference_document_type",
// 		"reference_document_name",
// 	],
// 	auto: true,
// 	cache: "oims:notifications",
// 	orderBy: "creation desc",
// 	onSuccess() {
// 		unreadNotificationsCount.reload()
// 	},
// })

export const arePushNotificationsEnabled = {
	data: [],
	loading: false,
	error: null,
	async reload() {
	},
}
// export const arePushNotificationsEnabled = createResource({
// 	url: "oims.api.are_push_notifications_enabled",
// 	cache: "oims:push_notifications_enabled",
// 	auto: true,
// })
