<template>
	<div class="flex flex-col gap-4 bg-white py-3 px-3.5 rounded-lg border-none">
		<div class="flex flex-col gap-1.5">
			<span class="text-gray-600 text-base font-medium leading-5">
				{{ __("Total Jumlah Makan Hari Ini") }}
			</span>
			<span class="text-gray-800 text-lg font-bold leading-6">
				{{ props.jumlah_makan }} Orang
			</span>
		</div>
	</div>
</template>

<script setup>
const props = defineProps({
	jumlah_makan: {
		type: Number
	},
})
</script>
