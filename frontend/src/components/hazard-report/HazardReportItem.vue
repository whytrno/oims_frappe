<template>
	<div class="bg-gray-200 rounded-xl border cursor-pointer">
		<div class="aspect-square w-full relative">
			<img
				:src="`https://oims.orecon.co.id${props.report.foto[0].foto}`"
				class="rounded-xl w-full h-full"
				alt="Report Image"
			/>
			<div class="absolute flex justify-between inset-0 p-2">
				<p class="bg-blue-600 rounded-full h-min text-xs p-2 text-white">
					{{ props.report.site }}
				</p>
				<p class="bg-blue-600 rounded-full h-min text-xs p-2 text-white">
					{{ props.report.status_temuan }}
				</p>
			</div>
		</div>
		<div class="p-2">
			<div class="flex justify-between font-semibold">
				<p class="w-min">{{ props.report.kategori_temuan }}</p>

				<div class="flex flex-col items-end">
					<p>{{ props.report.waktu }}</p>
					<p>{{ props.report.kode_bahaya }}</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { defineProps } from "vue"

const props = defineProps({
	report: {
		type: Object,
		required: true,
	},
})
</script>
