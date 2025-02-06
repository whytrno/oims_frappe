<template>
	<BaseLayout :pageTitle="__('Ambil Jatah Makan')">
		<template #body>
			<div class="flex flex-col mt-2 mb-7 p-4 gap-7 h-full relative">
				<JumlahMakanSummary :jumlah_makan="todayAmbilJatahMakanCount" />

				<div>
					<div class="flex flex-row justify-between items-center">
						<div class="text-lg text-gray-800 font-bold">
							{{ __("Karyawan") }}
						</div>
					</div>

					<JumlahMakanData :items="todayKaryawanAmbilJatahMakan" />
				</div>
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { loadingController } from "@ionic/vue"
import BaseLayout from "@/components/BaseLayout.vue"
import FuelingData from "@/components/FuelingData.vue"
import { advanceBalance } from "@/data/advances"
import { ref, onMounted } from "vue"
import { createResource } from "frappe-ui"
import JumlahMakanSummary from "../../components/jumlah-makan/JumlahMakanSummary.vue"
import JumlahMakanData from "../../components/jumlah-makan/JumlahMakanData.vue"

const todayKaryawanAmbilJatahMakan = ref([])
const todayAmbilJatahMakanCount = ref(0)

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Loading...",
	})
	loading.present()

	try {
		const todayKaryawanAmbilJatahMakanFetch = createResource({
			url: "oims.api.get_today_karyawan_makan",
			cache: "oims:get_today_karyawan_makan",
		})
		await todayKaryawanAmbilJatahMakanFetch.fetch()
		console.log(todayKaryawanAmbilJatahMakanFetch.data)
		todayKaryawanAmbilJatahMakan.value = todayKaryawanAmbilJatahMakanFetch.data

		todayAmbilJatahMakanCount.value = todayKaryawanAmbilJatahMakanFetch.data.length

		loading.dismiss()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})
</script>
