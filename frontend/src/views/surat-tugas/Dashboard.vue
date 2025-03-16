<template>
	<BaseLayout :pageTitle="__('Hazard Report Dashboard')">
		<template #body>
			<div class="p-4 gap-7 h-screen mb-14 relative space-y-5" v-for="report in hazardReports" :key="report.name">
				<router-link :to="{ name: 'HazardReportForm', params: { id: report.name } }">
					<HazardReportItem :report="report" />
				</router-link>
			</div>
			<div class="p-4 gap-7 h-screen mb-14 relative space-y-5">
				<router-link :to="{ name: 'SuratTugasDetail', params: { id: '15/41/ST/OSP/II/2025' } }">
					<div class="w-full p-5 flex justify-between rounded border border-gray-300 bg-white items-center">
						<div class="space-y-1">
							<p><span class="font-bold">No:</span> 15/41/ST/OSP/II/2025</p>
							<p><span class="font-bold">Site:</span> BDES</p>
						</div>
						<div>
							->
						</div>
					</div>
				</router-link>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { loadingController } from "@ionic/vue"
import BaseLayout from "@/components/BaseLayout.vue"
import { ref, onMounted } from "vue"
import HazardReportItem from "../../components/hazard-report/HazardReportItem.vue"
import { getAllSuratTugas } from "../../data/surat-tugas"

const suratTugas = ref({})

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Loading...",
	})
	loading.present()

	try {
		const fetchAllSuratTugas = getAllSuratTugas
		await fetchAllSuratTugas.fetch()
		suratTugas.value = fetchAllSuratTugas.data

		loading.dismiss()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})
</script>
