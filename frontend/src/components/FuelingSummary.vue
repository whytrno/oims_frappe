<template>
	<div class="flex flex-col gap-4 bg-white py-3 px-3.5 rounded-lg border-none" v-if="summary.data">
		<div class="flex flex-col gap-1.5">
			<span class="text-gray-600 text-base font-medium leading-5">
				{{ __("Total Pengeluaran Bahan Bakar Hari Ini") }}
			</span>
			<span class="text-gray-800 text-lg font-bold leading-6">
				{{ props.volume }} Litter
			</span>
		</div>
	</div>
</template>

<script setup>
import { expenseClaimSummary as summary } from "@/data/claims"

const props = defineProps({
	volume: {
		type: Number
	},
})
</script>
