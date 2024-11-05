import { createResource } from "frappe-ui"

export const companyCurrency = {
	data: [],
	loading: false,
	error: null,
	async reload() {
	},
}
// const companyCurrency = createResource({
// 	url: "oims.api.get_company_currencies",
// 	auto: true,
// })

export const currencySymbols = {
	data: [],
	loading: false,
	error: null,
	async reload() {
	},
}
// const currencySymbols = createResource({
// 	url: "oims.api.get_currency_symbols",
// 	auto: true,
// })

export function getCompanyCurrency(company) {
	return companyCurrency?.data?.[company]?.[0]
}

export function getCompanyCurrencySymbol(company) {
	return companyCurrency?.data?.[company]?.[1]
}

export function getCurrencySymbol(currency) {
	return currencySymbols?.data?.[currency]
}
