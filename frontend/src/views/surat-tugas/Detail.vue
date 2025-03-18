<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<div class="flex flex-col h-full w-full">
				<div class="w-full h-full bg-white sm:w-96 flex flex-col">
					<header class="flex flex-row bg-white shadow-sm py-4 px-3 items-center sticky top-0 z-[1000]">
						<Button variant="ghost" class="!pl-0 hover:bg-white" @click="router.back()">
							<FeatherIcon name="chevron-left" class="h-5 w-5" />
						</Button>
						<div class="flex flex-row items-center gap-2 overflow-hidden grow">
							<h2
								class="text-xl font-semibold text-gray-900 whitespace-nowrap overflow-hidden text-ellipsis">
								Detail Surat Tugas
							</h2>
							<Badge :label="suratTugas.sudah_di_tanda_tangani ? 'Sudah TTD' : 'Belum TTD'" :theme="suratTugas.sudah_di_tanda_tangani ? 'green' : 'red'" class="whitespace-nowrap text-[8px]"
								variant="outline" />
						</div>

						<Dropdown class="ml-auto" :options="[
							{
								label: __('Tanda Tangani'),
								onClick: tandaTangani,
							},
						]" :button="{
							label: __('Menu'),
							icon: 'more-horizontal',
							variant: 'ghost',
						}" />
					</header>
					<div class="bg-white grow overflow-y-auto">
						<div class="w-full overflow-auto flex justify-center h-full">
							<iframe class="h-full w-full"
								:src="`https://docs.google.com/gview?url=https://oims.orecon.co.id${suratTugas.file_url}&embedded=true`">
							</iframe>
						</div>
					</div>
					<!-- <Button variant="solid" class="py-7 w-full">
				Tanda Tangani
			</Button> -->
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent, loadingController } from "@ionic/vue"
import { Badge, FeatherIcon, Dropdown, createResource, createListResource } from "frappe-ui"
import { useRouter } from "vue-router"
import { ref, onMounted } from "vue"
import { getSuratTugasDocUrl, tandaTanganiSuratTugas } from "../../data/surat-tugas"
import { inject } from "vue"
const employee = inject("$employee")

const props = defineProps({
	name: {
		type: String,
		required: false,
	},
})

const suratTugas = ref({})
const router = useRouter()
const tandaTangani = async () => {
	const confirmation = confirm("Apakah anda yakin ingin menandatangani surat tugas ini?")

	if(confirmation){
		await tandaTanganiSuratTugas(employee.data.name, props.name)
	}
}

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
