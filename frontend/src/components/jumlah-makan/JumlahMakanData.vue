<template>
	<div class="flex flex-col gap-2.5 mt-5 overflow-auto">
		<JatahMakanItem v-for="item in items" :key="item.id" :item="item" />
	</div>
</template>

<script setup>
import JatahMakanItem from "./JumlahMakanItem.vue";

const props = defineProps({
	items: {
		type: Array,
	},
})
</script>
