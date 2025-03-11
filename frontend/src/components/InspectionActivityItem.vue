<template>
	<div class="bg-gray-200 rounded-xl border cursor-pointer">
		<div class="aspect-square w-full relative">
			<img :src="`https://oims.orecon.co.id${props.inspection.foto[0].foto}`"
				class="rounded-xl w-full h-full object-contain" alt="Report Image" />
			<div class="absolute flex justify-between inset-0 p-2">
				<p class="bg-blue-600 rounded-full h-min text-xs p-2 text-white">
					{{ props.inspection.site }}
				</p>
				<p class="bg-blue-600 rounded-full h-min text-xs p-2 text-white">
					{{ props.inspection.waktu }}
				</p>
			</div>
		</div>
		<div class="bg-blue-600 text-white text-sm p-2 text-center rounded-b-xl flex justify-center px-3">
			<p>{{ props.inspection.name }}</p>
		</div>
	</div>
</template>

<script setup>
import { defineProps } from "vue"

const props = defineProps({
	inspection: {
		type: Object,
		required: true,
	},
})

console.log(props.inspection)
</script>
