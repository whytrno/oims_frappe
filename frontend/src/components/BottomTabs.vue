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
import LeaveIcon from "@/components/icons/LeaveIcon.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"
import SalaryIcon from "@/components/icons/SalaryIcon.vue"
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
		role: [""]
	},
	{
		icon: AttendanceIcon,
		title: __("Kalendar Absen"),
		route: "/dashboard/attendance",
		role: [""]
	},
	{
		icon: FuelingIcon,
		title: __("Fueling"),
		route: "/dashboard/fueling",
		role: ["Fuelman"]
	},
	// {
	// 	icon: ShiftIcon,
	// 	title: __("Surat Tugas"),
	// 	route: "/dashboard/surat-tugas",
	// role: ["Fuelman"]
	// },
	// {
	// 	icon: ExpenseIcon,
	// 	title: __("Expenses"),
	// 	route: "/dashboard/expense-claims",
	// role: ["Fuelman"]
	// },
]

const filteredTabItems = computed(() => {
	// Ambil role pengguna dari $user
	const userRoles = employee.data?.jabatan || []

	// Kembalikan tab yang role-nya cocok atau role-nya null (tidak terbatas)
	return tabItems.filter(
		(item) => !item.role || userRoles.includes(item.role)
	)
})
</script>
