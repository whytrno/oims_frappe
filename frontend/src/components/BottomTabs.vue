<template>
	<ion-tab-bar
		slot="bottom"
		class="bg-white shadow-md sm:w-96 py-2 pb-2 standalone:pb-safe-bottom"
	>
		<ion-tab-button
			v-for="item in filteredTabItems"
			:key="item.title"
			:tab="item.title"
			:href="item.route"
			:class="[
				'bg-white text-xs !hover:border-gray-300 !hover:text-gray-700 transition active:scale-95',
				route.path === item.route
					? 'border-gray-900 text-gray-800 font-semibold'
					: 'text-gray-600 font-normal',
			]"
		>
			<router-link :to="item.route" class="flex flex-col space-y-1.5 items-center">
				<component :is="item.icon" class="h-5 w-5" />
				<div>{{ item.title }}</div>
			</router-link>
		</ion-tab-button>
	</ion-tab-bar>
</template>

<script setup>
import { useRoute } from "vue-router"

import { IonTabBar, IonTabButton, IonLabel } from "@ionic/vue"

const employee = inject("$employee")

import HomeIcon from "@/components/icons/HomeIcon.vue"
import ShiftIcon from "@/components/icons/ShiftIcon.vue"
import AttendanceIcon from "@/components/icons/AttendanceIcon.vue"
import { inject, computed } from "vue"
import FuelingIcon from "./icons/FuelingIcon.vue"

const __ = inject("$translate")

const route = useRoute()

const tabItems = [
	{
		icon: HomeIcon,
		title: __("Home"),
		route: "/home",
		jabatan: null
	},
	{
		icon: AttendanceIcon,
		title: __("Kalendar Absen"),
		route: "/dashboard/attendance",
		jabatan: null
	},
	{
		icon: FuelingIcon,
		title: __("Fueling"),
		route: "/dashboard/fueling",
		jabatan: ["Fuelman"]
	},
	{
		icon: ShiftIcon,
		title: __("Jumlah Makan"),
		route: "/dashboard/jumlah-makan",
		jabatan: ["Office Boy", "Gs", "Hr"]
	},
	// {
	// 	icon: ShiftIcon,
	// 	title: __("Surat Tugas"),
	// 	route: "/dashboard/surat-tugas",
	// 	jabatan: null
	// },
	// {
	// 	icon: ExpenseIcon,
	// 	title: __("Expenses"),
	// 	route: "/dashboard/expense-claims",
	// jabatan: ["Fuelman"]
	// },
]

const filteredTabItems = computed(() => {
	const userjabatans = employee.data?.jabatan || []

	// Kembalikan tab yang jabatan-nya cocok atau jabatan-nya null (tidak terbatas)
	return tabItems.filter(
		(item) => !item.jabatan || userjabatans.includes(item.jabatan)
	)
})
</script>
