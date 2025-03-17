<template>
	<BaseLayout :pageTitle="__('Surat Tugas Dashboard')">
		<template #body>
			<div class="p-4 gap-7 h-screen mb-14 relative space-y-3">
				<router-link v-for="surat in suratTugas" :to="{ name: 'SuratTugasDetail', params: { name: surat.name } }" class="w-full p-5 flex justify-between rounded border border-gray-300 bg-white items-center">
					<div class="space-y-1">
						<p><span class="font-bold">No:</span> {{ surat.name }}</p>
						<p><span class="font-bold">Site:</span> {{ surat.site }}</p>
						<p><span class="font-bold">Tanggal Dibuat:</span> {{ new Date(surat.creation).toISOString().split("T")[0] }}</p>
					</div>
					<div>
						->
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
