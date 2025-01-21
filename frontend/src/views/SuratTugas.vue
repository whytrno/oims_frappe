<template>
	<ion-page>
		<!-- <FormField
							v-for="field in expensesTableFields.data"
							:key="field.fieldname"
							class="w-full"
							:label="__(field.label, null, 'Expense Claim Detail')"
							:fieldtype="field.fieldtype"
							:fieldname="field.fieldname"
							:options="field.options"
							:hidden="field.hidden"
							:reqd="field.reqd"
							:default="field.default"
							:readOnly="field.read_only"
							/> -->
		<ListView
			doctype="Surat Tugas"
			:pageTitle="('Surat Tugas')"
			:tabButtons="TAB_BUTTONS"
			:fields="FIELDS"
			:filterConfig="FILTER_CONFIG"
		/>
	</ion-page>
</template>

<script setup>
import { IonPage } from "@ionic/vue"
import ListView from "@/components/ListView.vue"
import { createResource } from "frappe-ui"
import FormField from "@/components/FormField.vue"

// const expensesTableFields = createResource({
// 	url: "oims.api.get_doctype_fields",
// 	params: { doctype: "Surat Tugas" },
// 	transform(data) {
// 		console.log(data)
// 		const excludeFields = ["description_sb", "amounts_sb"]
// 		return data.filter((field) => !excludeFields.includes(field.fieldname))
// 	},
// })
// expensesTableFields.reload()

const TAB_BUTTONS = [
	{
		label: "Belum di TTD",
		fieldname: "tandatangan",
		condition: "not like",
		value: "data:%"
	},
	{
		label: "Sudah di TTD",
		fieldname: "tandatangan",
		condition: "like",
		value: "data:%"
	},
]

const FIELDS = [
	"no_surat",
	"tanggal_berangkat",
	"keperluan",
	"site",
	"karyawan_for_list_view",
	"tandatangan"
]

const FILTER_CONFIG = [
	{
		fieldname: "tandatangan",
		fieldtype: "Signature",
		label: "Tandatangan",
	},
]
</script>
