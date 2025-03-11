<template>
	<BaseLayout :pageTitle="__('Hazard Report Dashboard')">
		<template #body>
			<div class="p-4 gap-7 h-screen mb-14 relative space-y-5" v-for="inspection in inspectionActivities"
				:key="inspection.name">
				<router-link :to="{ name: 'InspectionActivityForm', params: { id: inspection.name } }">
					<InspectionActivityItem :inspection="inspection" />
				</router-link>
			</div>
			<div class="w-full sticky bottom-16 right-0 pt-4">
				<router-link :to="{ name: 'InspectionActivityForm' }" v-slot="{ navigate }">
					<Button @click="navigate" variant="solid" class="w-full py-5 text-base rounded-b-none">
						{{ __("Tambahkan Inspection Activity") }}
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
import InspectionActivityItem from "../../components/InspectionActivityItem.vue"
import { inspectionActivityResource } from "../../data/inspection-activity"

const inspectionActivities = ref({})

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Loading...",
	})
	loading.present()

	try {
		const fetchInspectionActivities = inspectionActivityResource
		await fetchInspectionActivities.fetch()
		inspectionActivities.value = fetchInspectionActivities.data
		loading.dismiss()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})
</script>
