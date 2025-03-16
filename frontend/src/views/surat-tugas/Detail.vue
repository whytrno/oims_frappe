<template>
	<BaseLayout :pageTitle="__('Hazard Report Dashboard')">
		<template #body>
			<div class="w-full overflow-auto flex justify-center">
				<div ref="viewerContainer" class="scale-50 w-full origin-top-left" />
			</div>
			<Button variant="solid" class="py-7 w-full">
				Tanda Tangani
			</Button>
		</template>
	</BaseLayout>
</template>

<script setup>
import BaseLayout from "@/components/BaseLayout.vue"
import { ref, onMounted } from "vue"
import * as docxParser from "docx-preview"

const viewerContainer = ref(null)

const renderDocx = async () => {
	try {
		const response = await fetch("https://oims.orecon.co.id/files/Cover Letter -Venti Kristian.docx")
		const blob = await response.blob()
		const arrayBuffer = await blob.arrayBuffer()
		docxParser.renderAsync(arrayBuffer, viewerContainer.value, null, {
			inWrapper: false,
			breakPages: false
		})
	} catch (error) {
		console.error("Gagal memuat file DOCX:", error)
	}
}

onMounted(renderDocx)
</script>
