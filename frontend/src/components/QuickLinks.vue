<template>
	<div class="flex flex-col gap-5 my-4 w-full">
		<div class="text-lg font-medium text-gray-900">{{ title || __("Menu") }}</div>
		<div class="grid grid-cols-4 gap-4">
			<router-link class="rounded-lg flex flex-col items-center gap-1 border border-2 p-1" :to="{ name: 'HazardReports' }">
				<FeatherIcon name="alert-triangle" class="h-8 w-8 text-blue-700" />
				<small class="text-center leading-4">Hazard Report</small>
			</router-link>
			<router-link class="rounded-lg flex flex-col items-center gap-1 border border-2 p-1" :to="{ name: 'FuelingDashboard' }">
				<FeatherIcon name="eye" class="h-8 w-8 text-blue-700" />
				<small class="text-center leading-4">Inspection</small>
			</router-link>
			<router-link class="rounded-lg flex flex-col items-center gap-1 border border-2 p-1" :to="{ name: 'FuelingDashboard' }">
				<FeatherIcon name="shield" class="h-8 w-8 text-blue-700" />
				<small class="text-center leading-4">Safety Talk</small>
			</router-link>
			<router-link class="rounded-lg flex flex-col items-center gap-1 border border-2 p-1" :to="{ name: 'FuelingDashboard' }">
				<FeatherIcon name="shield" class="h-8 w-8 text-blue-700" />
				<small class="text-center leading-4">Observation Activity</small>
			</router-link>
			<router-link class="rounded-lg flex flex-col items-center gap-1 border border-2 p-1" :to="{ name: 'FuelingDashboard' }">
				 <BarbellIcon />
				<small class="text-center leading-4">Sport Activity</small>
			</router-link>
		</div>
	</div>
</template>

<script setup>
import { FeatherIcon } from "frappe-ui"
import BarbellIcon from "./icons/BarbellIcon.vue";

const props = defineProps({
	title: {
		type: String,
		required: false,
		default: "",
	},
	items: {
		type: Array,
		required: true,
	},
})
</script>
