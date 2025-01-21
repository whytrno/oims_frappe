<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView
				doctype="Hazard Report"
				v-model="fuelingData"
				:isSubmittable="true"
				:fields="formFields"
				@validateForm="validateForm"
				childPhotoTable="Hazard Report Image"
				redirectToName="HazardReports"
				:id="props.id"
			/>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent, loadingController } from "@ionic/vue"
import { createResource, FeatherIcon } from "frappe-ui"
import { inject, ref, computed, defineProps, onMounted } from "vue"
import { useRouter } from "vue-router"
import FormView from "@/components/FormView.vue"
import { pushAfterFieldName } from "@/utils/pushObjectAfterFieldname"

const employee = inject("$employee")

const formFields = ref([])
const fuelingData = ref([])

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Mengambil data dari server...",
	})
	loading.present()

	try {
		const fieldsResponse = createResource({
			url: "oims.api.get_doctype_fields",
			params: { doctype: "Hazard Report" },
		})
		await fieldsResponse.fetch()
		formFields.value = fieldsResponse.data
		pushAfterFieldName(formFields.value, "status_temuan", {
			fieldname: "temuan",
			fieldtype: "Attach Image",
			label: "Foto Temuan",
		})
		pushAfterFieldName(formFields.value, "deskripsi_temuan", {
			fieldname: "tindakan",
			fieldtype: "Attach Image",
			label: "Foto Tindakan",
		})

		const karyawanField = formFields.value.find((field) => field.fieldname === "karyawan")
		if (karyawanField) {
			karyawanField.hidden = 1
		}

		fuelingData.value = {
			karyawan: employee.data.name,
		}
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})

// Function to validate and submit the form
function validateForm() {
	// Custom validation logic, if needed
	if (!fuelingData.value.volume_litter || !fuelingData.value.hm || !fuelingData.value.waktu) {
		alert("Please fill in the required fields.")
		return false
	}
	// Additional submit actions here if needed
	return true
}
</script>
