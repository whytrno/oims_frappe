<template>
	<BaseLayout :pageTitle="__('Fueling Dashboard')">
		<template #body>
			<div class="flex flex-col mt-2 mb-7 p-4 gap-7 h-full relative">
				<FuelingSummary :volume="todayFuelingVolume" />

				<div>
					<div class="flex flex-row justify-between items-center">
						<div class="text-lg text-gray-800 font-bold">
							{{ __("Pengisian Terbaru") }}
						</div>
						<!-- <router-link :to="{ name: 'EmployeeAdvanceListView' }"
							class="text-sm text-gray-800 font-semibold cursor-pointer underline underline-offset-2">
							{{ __("View List") }}
						</router-link> -->
					</div>

					<FuelingData :items="todayFueling" />
				</div>

				<div class="w-full absolute bottom-0 left-0 px-4">
					<router-link :to="{ name: 'FuelingScanQr' }" v-slot="{ navigate }">
						<Button @click="navigate" variant="solid" class="w-full py-5 text-base">
							{{ __("Tambahkan Pengisian Baru") }}
						</Button>
					</router-link>
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { loadingController } from "@ionic/vue";
import BaseLayout from "@/components/BaseLayout.vue"
import FuelingSummary from "@/components/FuelingSummary.vue"
import FuelingData from "@/components/FuelingData.vue"
import { advanceBalance } from "@/data/advances"
import { ref, onMounted } from "vue";
import { createResource } from "frappe-ui";

const todayFueling = ref([])
const todayFuelingVolume = ref(0)

onMounted(async () => {
	const loading = await loadingController.create({
		message: 'Loading...',
	});
	loading.present();

	try {
		const todayFuelingFetch = createResource({
			url: "minning_production.api.get_today_fueling_data",
			cache: "oims:today_fueling",
		});
		await todayFuelingFetch.fetch();
		todayFueling.value = todayFuelingFetch.data;

		const todayFuelingVolumeFetch = createResource({
			url: "minning_production.api.get_today_fueling_volume",
			cache: "oims:today_fueling_volume",
		});
		await todayFuelingVolumeFetch.fetch();
		todayFuelingVolume.value = todayFuelingVolumeFetch.data;

		loading.dismiss();
	} catch (error) {
		console.error("Error loading data:", error);
	} finally {
		loading.dismiss();
	}
});
</script>
