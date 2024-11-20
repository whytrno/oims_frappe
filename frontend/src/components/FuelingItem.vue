<template>
	<!-- <router-link :to="{ name: 'Attendance' }" v-slot="{ navigate }"> -->
		<ListItem class="p-3.5 bg-white rounded">
			<template #left>
				<FuelingIcon class="h-5 w-5 text-gray-500" />
				<div class="flex flex-col items-start gap-1.5">
					<!-- Parent data (dynamic) -->
					<div class="text-base font-normal text-gray-800">
						{{ item.parent }}
					</div>
					<!-- Volume and HM data (dynamic) -->
					<div class="text-xs font-normal text-gray-500">
						{{ item.volume_litter }} L | {{ item.hm }} HM
					</div>
				</div>
			</template>
			<template #right>
				<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
			</template>
		</ListItem>
	<!-- </router-link> -->
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"
import FuelingIcon from "./icons/FuelingIcon.vue";
import ListItem from "@/components/ListItem.vue"

// Terima item dari prop
const props = defineProps({
	item: {
		type: Object,
		required: true,
	},
});
</script>
