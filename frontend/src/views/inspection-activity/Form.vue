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
								Inspection Activity
							</h2>
							<Badge v-if="props.id" :label="props.id" class="whitespace-nowrap text-[8px]"
								variant="outline" />
						</div>

						<Dropdown class="ml-auto" :options="[
							{
								label: __('Delete'),
								condition: showUpdateDeleteButton,
								onClick: () => (showDeleteDialog = true),
							},
						]" :button="{
							label: __('Menu'),
							icon: 'more-horizontal',
							variant: 'ghost',
						}" />
					</header>

					<div class="bg-white grow overflow-y-auto">
						<div class="flex flex-col space-y-4 p-4">
							<FormField v-for="field in formFields" :key="field.fieldname" :fieldtype="field.fieldtype"
								:fieldname="field.fieldname" v-model="formModel[field.fieldname]"
								:default="field.default" :label="field.label" :options="field.options"
								:linkFilters="field.linkFilters" :documentList="field.documentList"
								:readOnly="isFieldReadOnly(field)" :reqd="Boolean(field.reqd)"
								:hidden="Boolean(field.hidden)" :errorMessage="field.error_message"
								:minDate="field.minDate" :maxDate="field.maxDate" :files="files" :accept="field.accept"
								:handleFileSelect="handleFileSelectForFiles"
								:handleFileDelete="handleFileDeleteForFiles" />
						</div>
					</div>

					<div v-if="showUpdateDeleteButton() || !props.id"
						class="px-4 pt-4 pb-4 standalone:pb-safe-bottom sm:w-96 bg-white sticky bottom-0 w-full drop-shadow-xl z-40 border-t rounded-t-lg">
						<ErrorMessage v-if="errorMessage" class="mb-2" :message="errorMessage" />

						<Button class="w-full rounded py-5 text-base disabled:bg-gray-700 disabled:text-white"
							@click="saveForm" :variant="formButton === 'Cancel' ? 'subtle' : 'solid'"
							:loading="isLoading">
							{{ props.id ? "Update" : "Save" }}
						</Button>
					</div>
				</div>
			</div>

			<Dialog v-model="showDeleteDialog">
				<template #body-title>
					<h2 class="text-xl font-bold">Inspection Activity</h2>
				</template>
				<template #body-content>
					<p>
						Are you sure you want to delete the Inspection Activity
						<span class="font-bold">{{ formModel.name }}</span>
						?
					</p>
				</template>
				<template #actions>
					<div class="flex flex-row gap-4">
						<Button variant="outline" class="py-5 w-full" @click="showDeleteDialog = false">
							Cancel
						</Button>
						<Button variant="solid" theme="red" @click="handleDocDelete" class="py-5 w-full">
							Delete
						</Button>
					</div>
				</template>
			</Dialog>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent, loadingController } from "@ionic/vue"
import { Badge, createResource, createListResource, FeatherIcon, toast, ErrorMessage, createDocumentResource, Dropdown, Dialog } from "frappe-ui"
import { inject, ref, defineProps, onMounted } from "vue"
import { pushAfterFieldName } from "@/utils/pushObjectAfterFieldname"
import FormField from "@/components/FormField.vue"
import { useRouter } from "vue-router"
import { FileAttachment } from "@/composables"

const employee = inject("$employee")
const router = useRouter()
const formFields = ref([])
const formModel = ref({})
const files = ref({})
const isLoading = ref(false)
const errorMessage = ref("")
const doctype = "Inspection Activities"
const redirectToName = "InspectionActivities"
const redirectParams = {}
let showDeleteDialog = ref(false)

const props = defineProps({
	id: {
		type: String,
		required: false,
	},
})

function showUpdateDeleteButton() {
	return props.id && formModel.value.docstatus !== 1 && formModel.value.owner == employee.data.user_id
}

onMounted(async () => {
	const loading = await loadingController.create({
		message: "Mengambil data dari server...",
	})
	loading.present()

	try {
		const fieldsResponse = createResource({
			url: "oims.api.get_doctype_fields",
			params: { doctype: doctype },
		})
		await fieldsResponse.fetch()
		formFields.value = fieldsResponse.data

		formFields.value.forEach(field => {
			formModel.value[field.fieldname] = field.default || ''
		})

		pushAfterFieldName(formFields.value, "keterangan_hasil_inspeksi", {
			fieldname: "inspeksi",
			fieldtype: "Attach Image",
			label: "Foto Inspeksi",
			accept: "image/*",
			reqd: 1,
		})
		files.value['inspeksi'] = []

		const karyawanField = formFields.value.find((field) => field.fieldname === "karyawan")
		if (karyawanField) {
			karyawanField.hidden = 1
			formModel.value[karyawanField.fieldname] = employee.data.name
		}

		if (props.id) {
			await loadDocument()
		}
	} catch (error) {
		errorMessage.value = "Error loading data"
	} finally {
		loading.dismiss()
	}
})

function isFieldReadOnly(field) {
	return Boolean(field.read_only)
}

function handleFileSelectForFiles(e, fieldName) {
	files.value[fieldName] = files.value[fieldName] || []
	files.value[fieldName].push(...e.target.files)
}

function handleFileDeleteForFiles(fileObj, fieldName) {
	files.value[fieldName] = files.value[fieldName].filter((file) => file.name !== fileObj.name)
}

function checkIsFileIsAttached(fieldName) {
	return files.value[fieldName] && files.value[fieldName].length
}

function validateMandatoryFields() {
	let errorFields = formFields.value
		.filter((field) => field.reqd && !field.hidden && !formModel.value[field.fieldname])

	errorFields.forEach((field) => {
		if (field.fieldtype === "Attach Image" && checkIsFileIsAttached(field.fieldname)) {
			errorFields = errorFields.filter((f) => f.fieldname !== field.fieldname)
		}
	})

	console.log(errorFields)
	const errorFieldLabels = errorFields.map((field) => field.label)

	if (errorFieldLabels.length) {
		errorMessage.value = `${errorFieldLabels.join(", ")} ${errorFieldLabels.length > 1 ? "fields are mandatory" : "field is mandatory"}`
		return false
	} else {
		errorMessage.value = ""
		return true
	}
}

function handleDocDelete() {
	documentResource.delete.submit()
	showDeleteDialog.value = false

	toast({
		title: "Success",
		text: `${doctype} deleted successfully!`,
		icon: "check-circle",
		position: "bottom-center",
		iconClasses: "text-green-500",
	})

	router.replace({
		name: redirectToName,
		params: redirectParams,
	})
}

async function saveForm() {
	if (!validateMandatoryFields()) return

	isLoading.value = true
	errorMessage.value = ""

	try {
		if (props.id) {
			await updateForm()
		} else {
			await createForm()
		}
	} catch (error) {
		errorMessage.value = "Error saving data"
	} finally {
		isLoading.value = false
	}
}

async function createForm() {
	docList.insert.submit(formModel.value)
}

async function updateForm() {
	try {
		await documentResource.setValue.submit(formModel.value)
		await documentResource.get.promise

		const attachImageFields = formFields.value
			.filter((field) => field.fieldtype === "Attach Image")
			.map((field) => field.fieldname)

		if (files.value) {
			for (const fieldName in files.value) {
				if (attachImageFields.includes(fieldName)) {
					if (files.value[fieldName].length !== 0) {
						files.value[fieldName] = files.value[fieldName].filter((file) => !file.idx)

						const uploadedFiles = await uploadAllAttachments(
							doctype,
							props.id,
							files.value[fieldName]
						)

						if (uploadedFiles.length !== 0) {
							await createResource({
								url: "oims.api.upload_files_to_inspection_activity_child_table",
								params: {
									name: props.id,
									files: uploadedFiles,
								},
							}).fetch()
						}
					}
				}
			}
		}

		toast({
			title: "Success",
			text: "Data updated successfully!",
			icon: "check-circle",
			position: "bottom-center",
			iconClasses: "text-green-500",
		})

		router.push({
			name: redirectToName,
			params: redirectParams,
		}).then(() => {
			window.location.reload()
		})
	} catch (error) {
		errorMessage.value = "Error updating data"
	}
}

async function uploadAllAttachments(documentType, documentName, attachments) {
	const uploadedFiles = []

	const uploadPromises = attachments.map((attachment) => {
		const fileAttachment = new FileAttachment(attachment)
		return fileAttachment.upload(documentType, documentName, "").then((fileDoc) => {
			fileDoc.uploaded = true

			const fileUrl = fileDoc.file_url
			if (fileUrl) {
				uploadedFiles.push(fileUrl)
			}

			if (props.id) {
				files.value.push(fileDoc)
			}
		})
	})
	await Promise.allSettled(uploadPromises)

	return uploadedFiles
}

const docList = createListResource({
	doctype: doctype,
	insert: {
		async onSuccess(data) {
			toast({
				title: "Success",
				text: `${doctype} created successfully!`,
				icon: "check-circle",
				position: "bottom-center",
				iconClasses: "text-green-500",
			})

			const attachImageFields = formFields.value
				.filter((field) => field.fieldtype === "Attach Image")
				.map((field) => field.fieldname)

			if (files.value) {
				for (const fieldName in files.value) {
					if (attachImageFields.includes(fieldName)) {
						if (files.value[fieldName].length !== 0) {
							const uploadedFiles = await uploadAllAttachments(
								data.doctype,
								data.name,
								files.value[fieldName]
							)

							if (uploadedFiles.length !== 0) {
								const fieldNameUpper = fieldName.charAt(0).toUpperCase() + fieldName.slice(1)

								createResource({
									url: "oims.api.upload_files_to_inspection_activity_child_table",
									params: {
										name: data.name,
										files: uploadedFiles,
										jenis: fieldNameUpper,
									},
								}).fetch()
							}
						}
					}
				}
			}

			if (redirectToName) {
				router.replace({
					name: redirectToName,
					params: redirectParams,
				})
			} else {
				router.replace({
					name: `${doctype.replace(/\s+/g, "")}DetailView`,
					params: { id: data.name },
				})
			}
		},
		onError() {
			toast({
				title: "Error",
				text: `Error creating ${doctype}`,
				icon: "alert-circle",
				position: "bottom-center",
				iconClasses: "text-red-500",
			})
		},
	},
})

const documentResource = createDocumentResource({
	doctype: doctype,
	name: props.id,
	fields: "*",
	setValue: {
		onSuccess() {
			toast({
				title: "Success",
				text: `${doctype} updated successfully!`,
				icon: "check-circle",
				position: "bottom-center",
				iconClasses: "text-green-500",
			})
		},
		onError() {
			toast({
				title: "Error",
				text: `Error updating ${doctype}`,
				icon: "alert-circle",
				position: "bottom-center",
				iconClasses: "text-red-500",
			})
		},
	},
})

async function loadDocument() {
	await documentResource.get.promise
	formModel.value = { ...documentResource.doc }
	documentResource.doc.foto.forEach((file) => {
		file.file_url = file.foto
		files.value['inspeksi'].push(file)
	})
}
</script>
