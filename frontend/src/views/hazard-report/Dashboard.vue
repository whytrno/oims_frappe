<template>
	<BaseLayout :pageTitle="__('Hazard Report Dashboard')">
		<template #body>
			<div
				class="p-4 gap-7 h-screen mb-2 relative space-y-5"
				v-for="report in hazardReports"
				:key="report.name"
			>
				<router-link :to="{ name: 'HazardReportForm', params: { id: report.name } }">
					<HazardReportItem :report="report" />
				</router-link>
			</div>
			<div class="w-full sticky bottom-16 right-0 pt-4">
				<router-link :to="{ name: 'HazardReportForm' }" v-slot="{ navigate }">
					<Button @click="navigate" variant="solid" class="w-full py-5 text-base rounded-b-none">
						{{ __("Tambahkan Hazard Report") }}
					</Button>
				</router-link>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { loadingController } from "@ionic/vue"
import BaseLayout from "@/components/BaseLayout.vue"
import { ref, onMounted } from "vue"
import { createResource } from "frappe-ui"
import HazardReportItem from "../../components/hazard-report/HazardReportItem.vue"
import { hazardReportsResource } from "@/data/hazard-report"

const hazardReports = ref({})

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Loading...",
	})
	loading.present()

	try {
		const fetchHazardReports = hazardReportsResource
		await fetchHazardReports.fetch()
		hazardReports.value = fetchHazardReports.data

		loading.dismiss()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})
</script>
