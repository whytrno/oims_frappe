<template>
	<div class="flex flex-col gap-2.5 mt-5 overflow-auto">
		<FuelingItem v-for="item in items" :key="item.id" :item="item" />
	</div>
</template>

<script setup>
import FuelingItem from "@/components/FuelingItem.vue"

const props = defineProps({
	items: {
		type: Array,
	},
})
</script>
