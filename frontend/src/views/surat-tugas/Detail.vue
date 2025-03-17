<template>
	<BaseLayout :pageTitle="__('Hazard Report Dashboard')">
		<template #body>
			<div class="w-full overflow-auto flex justify-center h-full">
				<iframe
				class="h-full w-full"
				:src="`https://docs.google.com/gview?url=https://oims.orecon.co.id${suratTugas.file_url}&embedded=true`">
				</iframe>
			</div>
			<Button variant="solid" class="py-7 w-full">
				Tanda Tangani
			</Button>
		</template>
	</BaseLayout>
</template>

<script setup>
import { loadingController } from "@ionic/vue"
import BaseLayout from "@/components/BaseLayout.vue"
import { ref, onMounted } from "vue"
import { getSuratTugasDocUrl } from "../../data/surat-tugas"

const props = defineProps({
	name: {
		type: String,
		required: false,
	},
})

const suratTugas = ref({})

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Loading...",
	})
	loading.present()

	try {
		const fetchSuratTugasDetail = getSuratTugasDocUrl(props.name)
		await fetchSuratTugasDetail.fetch()
		suratTugas.value = fetchSuratTugasDetail.data

		loading.dismiss()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})
</script>
