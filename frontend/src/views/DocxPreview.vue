<template>
	<div ref="viewerContainer" class="docx-container"></div>
</template>

<script setup>
import { ref, onMounted } from "vue"
import * as docxParser from "docx-preview" // Named import

const viewerContainer = ref(null)

const renderDocx = async () => {
	try {
		const response = await fetch("/tes.docx") // Ambil file dari public/
		const blob = await response.blob()
		const arrayBuffer = await blob.arrayBuffer()
		docxParser.renderAsync(arrayBuffer, viewerContainer.value) // Perbaiki pemanggilan fungsi
	} catch (error) {
		console.error("Gagal memuat file DOCX:", error)
	}
}

onMounted(renderDocx)
</script>

<style>
.docx-container {
	border: 1px solid #ddd;
	padding: 10px;
	overflow: auto;
	max-height: 500px;
	background: white;
}
</style>
