<template>
	<div v-if="showField" class="flex flex-col gap-1.5">
		<!-- Label -->
		<span v-if="!['Check', 'Section Break', 'Column Break'].includes(props.fieldtype)" :class="[
			// mark field as mandatory
			props.reqd ? `after:content-['_*'] after:text-red-600` : ``,
			`block text-sm leading-5 text-gray-700`,
		]">
			{{ props.label }}
		</span>

		<!-- Select or Link field with predefined options -->
		<Autocomplete v-if="props.fieldtype === 'Select' || props.documentList"
			:class="isReadOnly ? 'pointer-events-none' : ''" :placeholder="__('Select {0}', [props.label])"
			:options="selectionList" :modelValue="modelValue" v-bind="$attrs" :disabled="isReadOnly"
			@update:modelValue="(v) => emit('update:modelValue', v?.value)" />

		<!-- Link field -->
		<Link v-else-if="props.fieldtype === 'Link'" :doctype="props.options" :modelValue="modelValue"
			:filters="props.linkFilters" :disabled="isReadOnly"
			@update:modelValue="(v) => emit('update:modelValue', v)" />

		<!-- Text -->
		<Input v-else-if="['Text Editor', 'Small Text', 'Text', 'Long Text'].includes(props.fieldtype)" type="textarea"
			:value="modelValue" :placeholder="__('Enter {0}', [props.label])"
			@input="(v) => emit('update:modelValue', v)" @change="(v) => emit('change', v)" v-bind="$attrs"
			:disabled="isReadOnly" class="h-15" />

		<!-- Check -->
		<Input v-else-if="props.fieldtype === 'Check'" type="checkbox" :label="props.label" :value="modelValue"
			@input="(v) => emit('update:modelValue', v)" @change="(v) => emit('change', v)" v-bind="$attrs"
			:disabled="isReadOnly" class="rounded-sm text-gray-800" />

		<!-- Data field -->
		<Input v-else-if="props.fieldtype === 'Data'" type="text" :value="modelValue"
			@input="(v) => emit('update:modelValue', v)" @change="(v) => emit('change', v)" v-bind="$attrs"
			:disabled="isReadOnly" />

		<!-- Read only currency field -->
		<Input v-else-if="props.fieldtype === 'Currency' && isReadOnly" type="text" :value="modelValue"
			@input="(v) => emit('update:modelValue', v)" @change="(v) => emit('change', v)" v-bind="$attrs"
			:disabled="isReadOnly" />

		<!-- Float/Int field -->
		<Input v-else-if="isNumberType" type="number" :value="modelValue" @input="(v) => emit('update:modelValue', v)"
			@change="(v) => emit('change', v)" v-bind="$attrs" :disabled="isReadOnly" />

		<!-- Section Break -->
		<!-- <div v-else-if="props.fieldtype === 'Section Break'" :class="props.addSectionPadding ? 'mt-2' : ''">
			<h2 v-if="props.label" class="text-base font-semibold text-gray-800"
				:class="props.addSectionPadding ? 'pt-4' : ''">
				{{ props.label }}
			</h2>
		</div> -->

		<!-- Date -->
		<!-- FIXME: default datepicker has poor UI -->
		<Input v-else-if="props.fieldtype === 'Date'" type="date" :value="modelValue"
			:placeholder="__('Select {0}', [props.label])" :formatValue="(val) => dayjs(val).format('DD-MM-YYYY')"
			@input="(v) => emit('update:modelValue', v)" @change="(v) => emit('change', v)" v-bind="$attrs"
			:disabled="isReadOnly" :min="props.minDate" :max="props.maxDate" />

		<!-- Time -->
		<!-- Datetime -->
		<DateTimePicker v-else-if="props.fieldtype === 'Datetime'" :value="modelValue"
			:placeholder="`Select ${props.label}`" :formatter="(val) => dayjs(val).format('DD-MM-YYYY HH:mm:ss')"
			@update:modelValue="(v) => emit('update:modelValue', v)" v-bind="$attrs" :disabled="isReadOnly" />

		<!-- <div class="flex flex-row gap-2 items-center justify-center p-5" v-if="isFileUploading">
			<LoadingIndicator class="w-3 h-3 text-gray-800" />
			<span class="text-gray-900 text-sm">{{ __("Uploading...") }} </span>
		</div> -->

		<VueSignaturePad v-else-if="props.fieldtype === 'Signature'" ref="signature" height="400px" width="950px"
			:max-width="options.maxWidth" :min-width="options.minWidth" :options="{
				penColor: options.penColor,
				backgroundColor: options.backgroundColor,
			}" />

		<FileUploaderView v-else-if="props.fieldtype === 'Attach Image'" v-model="props.files" :accept="props.accept"
			@handleFileSelect="handleFileSelect($event, props.fieldname)"
			@handleFileDelete="handleFileDelete($event, props.fieldname)" :usingTitle="false"
			:fieldName="props.fieldname" />

		<ErrorMessage :message="props.errorMessage" />
	</div>
</template>

<script setup>
import { Autocomplete, DateTimePicker, ErrorMessage, Input } from "frappe-ui"
import { computed, onMounted, inject, ref, watch } from "vue"
import FileUploaderView from "@/components/FileUploaderView.vue"
import { VueSignaturePad } from "@selemondev/vue3-signature-pad"
import { FileAttachment } from "@/composables"

import Link from "@/components/Link.vue"

const __ = inject("$translate")
const options = ref({
	penColor: "rgb(0,0,0)",
	backgroundColor: "rgb(255, 255, 255)",
	maxWidth: 2,
	minWidth: 2,
})
const signature = ref()
// let fileAttachments = ref([])

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
// 		fileAttachments.value = fileAttachments.value.filter((file) => file.name !== fileObj.name)
// 	}
// }

function handleUndo() {
	return signature.value?.undo && signature.value?.undo()
}

function handleClearCanvas() {
	return signature.value?.clearCanvas && signature.value?.clearCanvas()
}

function handleSaveSignature() {
	return signature.value?.saveSignature && alert(signature.value?.saveSignature())
}

const props = defineProps({
	fieldtype: String,
	fieldname: String,
	modelValue: [String, Number, Boolean, Array, Object],
	default: [String, Number, Boolean, Array, Object],
	label: String,
	options: [String, Array],
	linkFilters: Object,
	documentList: Array,
	readOnly: [Boolean, Number],
	reqd: [Boolean, Number],
	hidden: {
		type: [Boolean, Number],
		default: false,
	},
	errorMessage: String,
	minDate: String,
	maxDate: String,
	addSectionPadding: {
		type: Boolean,
		default: true,
	},
	files: Array,
	accept: {
		type: String,
		default: "*",
	},
	handleFileSelect: Function,
	handleFileDelete: Function,
})

const emit = defineEmits(["change", "update:modelValue"])
const dayjs = inject("$dayjs")

// Signature pad-related logic
// const signatureCanvas = ref(null)
// const signaturePad = ref(null)
// const canvasWidth = 400
// const canvasHeight = 200
// let isDrawing = false

const showField = computed(() => {
	if (props.fieldtype === "Attach Image") return true
	if (props.readOnly && !isLayoutField.value && !props.modelValue) return false

	return props.fieldtype !== "Table" && !props.hidden
})

const isNumberType = computed(() => {
	return ["Int", "Float", "Currency"].includes(props.fieldtype)
})

const isLayoutField = computed(() => {
	return ["Section Break", "Column Break"].includes(props.fieldtype)
})

const isReadOnly = computed(() => {
	return Boolean(props.readOnly)
})

const selectionList = computed(() => {
	if (props.fieldtype === "Link" && props.documentList) {
		return props.documentList
	} else if (props.fieldtype == "Select" && props.options) {
		const options = props.options.split("\n")
		return options.map((option) => ({
			label: __(option),
			value: option,
		}))
	}

	return []
})

function setDefaultValue() {
	// set default values
	if (props.modelValue) return

	if (props.default) {
		if (props.fieldtype === "Check") {
			emit("update:modelValue", props.default === "1" ? true : false)
		} else if (props.fieldtype === "Date" && props.default === "Today") {
			emit("update:modelValue", dayjs().format("YYYY-MM-DD"))
		} else if (isNumberType.value) {
			emit("update:modelValue", parseFloat(props.default || 0))
		} else {
			emit("update:modelValue", props.default)
		}
	} else {
		props.fieldtype === "Check" ? emit("update:modelValue", false) : emit("update:modelValue", "")
	}
}

onMounted(() => {
	setDefaultValue()
})
</script>
