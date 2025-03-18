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
							<Badge :label="suratTugas.sudah_di_tanda_tangani ? 'Sudah TTD' : 'Belum TTD'"
								:theme="suratTugas.sudah_di_tanda_tangani ? 'green' : 'red'"
								class="whitespace-nowrap text-[8px]" variant="outline" />
						</div>

					</header>
					<div class="bg-white grow overflow-y-auto relative">
						<div class="w-full overflow-auto flex justify-center h-full">
							<iframe v-if="suratTugas.sudah_di_tanda_tangani" class="h-full w-full"
								:src="`https://docs.google.com/gview?url=https://oims.orecon.co.id${docUrl.file_url}?time=0&embedded=true`">
							</iframe>
							<iframe v-else class="h-full w-full"
								:src="`https://view.officeapps.live.com/op/embed.aspx?src=https://oims.orecon.co.id${docUrl.file_url}`">
							</iframe>
						</div>

						<button @click="tandaTangani" :disabled="suratTugas.sudah_di_tanda_tangani || loading"
							class="absolute bottom-3 right-3 size-14 rounded-xl bg-white shadow-xl flex items-center justify-center disabled:bg-gray-600">
							<FeatherIcon v-if="!loading" name="pen-tool" class="size-7" />
							<FeatherIcon v-else name="loader" class="size-7 animate-spin" />
						</button>
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
const docUrl = ref("")
const router = useRouter()
const loading = ref(false)

const fetchSuratTugasDetail = createListResource({
	doctype: "Surat Tugas",
	fields: ["*"],
	filters: {
		name: props.name,
	},
})

const tandaTangani = async () => {
	const confirmation = confirm("Apakah anda yakin ingin menandatangani surat tugas ini?")

	if (confirmation) {
		loading.value = true
		await tandaTanganiSuratTugas(employee.data.name, props.name)

		await fetchSuratTugasDetail.setValue.submit({
			name: props.name,
			sudah_di_tanda_tangani: 1,
			ditanda_tangani_oleh: employee.data.name,
		})
		loading.value = false
	}
}

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Loading...",
	})
	loading.present()

	try {
		await fetchSuratTugasDetail.reload()
		const fetchSuratTugasDocUrl = getSuratTugasDocUrl(props.name)
		await fetchSuratTugasDocUrl.fetch()

		suratTugas.value = fetchSuratTugasDetail.data[0]
		docUrl.value = fetchSuratTugasDocUrl.data

		loading.dismiss()
	} catch (error) {
		console.error("Error loading data:", error)
	} finally {
		loading.dismiss()
	}
})
</script>
