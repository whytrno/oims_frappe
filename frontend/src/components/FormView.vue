<template>
	<div></div>
</template>

<script setup>
// import { computed, nextTick, onMounted, ref, watch } from "vue"
// import { useRouter } from "vue-router"
// import {
// 	ErrorMessage,
// 	Badge,
// 	FeatherIcon,
// 	createListResource,
// 	createDocumentResource,
// 	toast,
// 	createResource,
// 	Dropdown,
// 	Dialog,
// 	LoadingIndicator,
// } from "frappe-ui"
// import FormField from "@/components/FormField.vue"
// import FileUploaderView from "@/components/FileUploaderView.vue"
// import WorkflowActionSheet from "@/components/WorkflowActionSheet.vue"

// import { FileAttachment, guessStatusColor } from "@/composables"
// import useWorkflow from "@/composables/workflow"
// // import { getCompanyCurrency } from "@/data/currencies"
// // import { formatCurrency } from "@/utils/formatters"

// const props = defineProps({
// 	doctype: {
// 		type: String,
// 		required: true,
// 	},
// 	modelValue: {
// 		type: Object,
// 		required: true,
// 	},
// 	isSubmittable: {
// 		type: Boolean,
// 		required: false,
// 		default: false,
// 	},
// 	fields: {
// 		type: Array,
// 		required: true,
// 	},
// 	id: {
// 		type: String,
// 		required: false,
// 	},
// 	tabbedView: {
// 		type: Boolean,
// 		required: false,
// 		default: false,
// 	},
// 	tabs: {
// 		type: Array,
// 		required: false,
// 	},
// 	showAttachmentView: {
// 		type: Boolean,
// 		required: false,
// 		default: false,
// 	},
// 	showFormButton: {
// 		type: Boolean,
// 		required: false,
// 		default: true,
// 	},
// })
// const emit = defineEmits(["validateForm", "update:modelValue"])
// const router = useRouter()
// let activeTab = ref(props.tabs?.[0].name)
// let fileAttachments = ref([])
// let statusColor = ref("")
// let formErrorMessage = ref("")
// let isFormDirty = ref(false)
// let isFormUpdated = ref(false)
// let showDeleteDialog = ref(false)
// let showSubmitDialog = ref(false)
// let showCancelDialog = ref(false)
// let isFileUploading = ref(false)
// let workflow = ref(null)

// const formModel = computed({
// 	get() {
// 		return props.modelValue
// 	},
// 	set(newValue) {
// 		emit("update:modelValue", newValue)
// 	},
// })

// const status = computed(() => {
// 	if (!props.id) return ""

// 	if (workflow.value) {
// 		const stateField = workflow.value.getWorkflowStateField()
// 		if (stateField) return formModel.value[stateField]
// 	}

// 	return formModel.value.status || formModel.value.approval_status
// })

// watch(
// 	() => formModel.value,
// 	() => {
// 		if (!props.id) return

// 		if (isFormReady.value && !isFormUpdated.value) {
// 			isFormDirty.value = true
// 		} else if (isFormUpdated.value) {
// 			isFormUpdated.value = false
// 		}
// 	},
// 	{ deep: true }
// )

// watch(
// 	() => status.value,
// 	async (value) => {
// 		if (!value) return
// 		statusColor.value = await guessStatusColor(props.doctype, status.value)
// 	},
// 	{ immediate: true }
// )

// const tabFields = computed(() => {
// 	let fieldsByTab = {}
// 	let fieldList = []
// 	let firstFieldIndex = 0
// 	let lastFieldIndex = 0

// 	props.tabs?.forEach((tab) => {
// 		lastFieldIndex = props.fields.findIndex(
// 			(field) => field.fieldname === tab.lastField
// 		)
// 		fieldList = props.fields.slice(firstFieldIndex, lastFieldIndex + 1)
// 		fieldsByTab[tab.name] = fieldList
// 		firstFieldIndex = lastFieldIndex + 1
// 	})

// 	return fieldsByTab
// })

// const attachedFiles = createResource({
// 	url: "oims.api.get_attachments",
// 	params: {
// 		dt: props.doctype,
// 		dn: props.id,
// 	},
// 	transform(data) {
// 		return data.map((file) => (file.uploaded = true))
// 	},
// 	onSuccess(data) {
// 		fileAttachments.value = data
// 	},
// })

// const handleFileSelect = (e) => {
// 	if (props.id) {
// 		uploadAllAttachments(props.doctype, props.id, [...e.target.files])
// 	} else {
// 		fileAttachments.value.push(...e.target.files)
// 	}
// }

// const handleFileDelete = async (fileObj) => {
// 	if (fileObj.uploaded) {
// 		const fileAttachment = new FileAttachment(fileObj)
// 		await fileAttachment.delete()
// 		await attachedFiles.reload()
// 	} else {
// 		fileAttachments.value = fileAttachments.value.filter(
// 			(file) => file.name !== fileObj.name
// 		)
// 	}
// }

// async function uploadAllAttachments(documentType, documentName, attachments) {
// 	isFileUploading.value = true

// 	const uploadPromises = attachments.map((attachment) => {
// 		const fileAttachment = new FileAttachment(attachment)
// 		return fileAttachment
// 			.upload(documentType, documentName, "")
// 			.then((fileDoc) => {
// 				fileDoc.uploaded = true
// 				if (props.id) {
// 					fileAttachments.value.push(fileDoc)
// 				}
// 			})
// 	})

// 	await Promise.allSettled(uploadPromises)
// 	isFileUploading.value = false
// }

// // CRUD for doc
// const docList = createListResource({
// 	doctype: props.doctype,
// 	insert: {
// 		async onSuccess(data) {
// 			toast({
// 				title: "Success",
// 				text: `${props.doctype} created successfully!`,
// 				icon: "check-circle",
// 				position: "bottom-center",
// 				iconClasses: "text-green-500",
// 			})
// 			await uploadAllAttachments(data.doctype, data.name, fileAttachments.value)

// 			router.replace({
// 				name: `${props.doctype.replace(/\s+/g, "")}DetailView`,
// 				params: { id: data.name },
// 			})
// 		},
// 		onError() {
// 			toast({
// 				title: "Error",
// 				text: `Error creating ${props.doctype}`,
// 				icon: "alert-circle",
// 				position: "bottom-center",
// 				iconClasses: "text-red-500",
// 			})
// 			console.log(`Error creating ${props.doctype}`)
// 		},
// 	},
// })

// const documentResource = createDocumentResource({
// 	doctype: props.doctype,
// 	name: props.id,
// 	fields: "*",
// 	setValue: {
// 		onSuccess() {
// 			toast({
// 				title: "Success",
// 				text: `${props.doctype} updated successfully!`,
// 				icon: "check-circle",
// 				position: "bottom-center",
// 				iconClasses: "text-green-500",
// 			})
// 		},
// 		onError() {
// 			toast({
// 				title: "Error",
// 				text: `Error updating ${props.doctype}`,
// 				icon: "alert-circle",
// 				position: "bottom-center",
// 				iconClasses: "text-red-500",
// 			})
// 			console.log(`Error updating ${props.doctype}`)
// 		},
// 	},
// 	delete: {
// 		onSuccess() {
// 			router.back()
// 			toast({
// 				title: "Success",
// 				text: `${props.doctype} deleted successfully!`,
// 				icon: "check-circle",
// 				position: "bottom-center",
// 				iconClasses: "text-green-500",
// 			})
// 		},
// 		onError() {
// 			toast({
// 				title: "Error",
// 				text: `Error deleting ${props.doctype}`,
// 				icon: "alert-circle",
// 				position: "bottom-center",
// 				iconClasses: "text-red-500",
// 			})
// 			console.log(`Error deleting ${props.doctype}`)
// 		},
// 	},
// })

// const docPermissions = createResource({
// 	url: "frappe.client.get_doc_permissions",
// 	params: { doctype: props.doctype, docname: props.id },
// })

// const permittedWriteFields = createResource({
// 	url: "oims.api.get_permitted_fields_for_write",
// 	params: { doctype: props.doctype },
// })

// const formButton = computed(() => {
// 	if (!props.showFormButton) return

// 	if (props.id && props.isSubmittable && !isFormDirty.value) {
// 		if (formModel.value.docstatus === 0 && hasPermission("submit")) {
// 			return "Submit"
// 		} else if (formModel.value.docstatus === 1 && hasPermission("cancel")) {
// 			return "Cancel"
// 		}
// 	} else if (formModel.value.docstatus !== 2) {
// 		return "Save"
// 	}
// })

// function showDeleteButton() {
// 	return props.id && formModel.value.docstatus !== 1 && hasPermission("delete")
// }

// function hasPermission(action) {
// 	return docPermissions.data?.permissions[action]
// }

// function isFieldReadOnly(field) {
// 	return (
// 		Boolean(field.read_only)
// 		|| isFormReadOnly.value
// 		|| (props.id && !permittedWriteFields.data?.includes(field.fieldname))
// 	)
// }

// function handleDocInsert() {
// 	if (!validateMandatoryFields()) return
// 	docList.insert.submit(formModel.value)
// }

// function validateMandatoryFields() {
// 	const errorFields = props.fields
// 		.filter(
// 			(field) =>
// 				field.reqd && !field.hidden && !formModel.value[field.fieldname]
// 		)
// 		.map((field) => field.label)

// 	if (errorFields.length) {
// 		formErrorMessage.value = `${errorFields.join(", ")} ${
// 			errorFields.length > 1 ? "fields are mandatory" : "field is mandatory"
// 		}`
// 		return false
// 	} else {
// 		formErrorMessage.value = ""
// 		return true
// 	}
// }

// async function handleDocUpdate(action) {
// 	if (documentResource.doc) {
// 		let params = { ...formModel.value }

// 		if (!validateMandatoryFields()) return

// 		if (action == "submit") {
// 			params.docstatus = 1
// 		} else if (action == "cancel") {
// 			params.docstatus = 2
// 		}

// 		await documentResource.setValue.submit(params)
// 		await documentResource.get.promise
// 		resetForm()
// 	}

// 	if (action === "submit") showSubmitDialog.value = false
// 	else if (action === "cancel") showCancelDialog.value = false
// }

// function saveForm() {
// 	emit("validateForm")

// 	if (props.id) {
// 		handleDocUpdate()
// 	} else {
// 		handleDocInsert()
// 	}
// }

// function submitOrCancelForm() {
// 	if (isFormDirty.value) return

// 	if (formModel.value.docstatus === 0) {
// 		emit("validateForm")
// 		showSubmitDialog.value = true
// 	} else if (formModel.value.docstatus === 1) {
// 		showCancelDialog.value = true
// 	}
// }

// function handleDocDelete() {
// 	documentResource.delete.submit()
// 	showDeleteDialog.value = false
// }

// async function reloadDoc() {
// 	await documentResource.reload()
// 	resetForm()
// }

// function resetForm() {
// 	formModel.value = { ...documentResource.doc }
// 	nextTick(() => {
// 		isFormDirty.value = false
// 		isFormUpdated.value = true
// 	})
// }

// async function setFormattedCurrency() {
// 	const companyCurrency = await getCompanyCurrency(formModel.value.company)

// 	props.fields.forEach((field) => {
// 		if (field.fieldtype !== "Currency") return
// 		if (!(field.readOnly || isFormReadOnly.value)) return

// 		if (field.options === "currency") {
// 			formModel.value[field.fieldname] = formatCurrency(
// 				formModel.value[field.fieldname],
// 				formModel.value.currency
// 			)
// 		} else {
// 			formModel.value[field.fieldname] = formatCurrency(
// 				formModel.value[field.fieldname],
// 				companyCurrency
// 			)
// 		}
// 	})
// }

// const isFormReadOnly = computed(() => {
// 	if (!isFormReady.value) return true
// 	if (!props.id) return false

// 	// submitted & cancelled docs are read only
// 	if (formModel.value.docstatus !== 0) return true

// 	// read only due to workflow based on current user's roles
// 	if (workflow.value?.isReadOnly(formModel.value)) return true
// })

// const isFormReady = computed(() => {
// 	if (!props.id) return true

// 	return !documentResource.get.loading && documentResource.doc
// })

// onMounted(async () => {
// 	if (props.id) {
// 		await documentResource.get.promise
// 		formModel.value = { ...documentResource.doc }
// 		await docPermissions.reload()
// 		await permittedWriteFields.reload()
// 		await attachedFiles.reload()
// 		await setFormattedCurrency()

// 		// workflow
// 		workflow.value = useWorkflow(props.doctype)

// 		isFormDirty.value = false
// 	}
// })
</script>
