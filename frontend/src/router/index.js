import { createRouter, createWebHistory } from "@ionic/vue-router"

import TabbedView from "@/views/TabbedView.vue"
import attendanceRoutes from "./attendance"
import claimRoutes from "./claims"
import employeeAdvanceRoutes from "./advances"

const routes = [
	{
		path: "/",
		redirect: "/home",
	},
	{
		path: "/",
		component: TabbedView,
		children: [
			{
				path: "",
				redirect: "/home",
			},
			{
				path: "/dashboard/surat-tugas",
				name: "SuratTugas",
				component: () => import("@/views/SuratTugas.vue"),
			},
			{
				path: "/home",
				name: "Home",
				component: () => import("@/views/Home.vue"),
			},
			{
				path: "/dashboard/attendance",
				name: "AttendanceDashboard",
				component: () => import("@/views/attendance/Dashboard.vue"),
			},
			{
				path: "/dashboard/fueling",
				name: "FuelingDashboard",
				component: () => import("@/views/fueling/Dashboard.vue"),
			},
			{
				path: "/dashboard/expense-claims",
				name: "ExpenseClaimsDashboard",
				component: () => import("@/views/expense_claim/Dashboard.vue"),
			},
		],
	},
	{
		path: "/dashboard/fueling/scan-qr",
		name: "FuelingScanQr",
		component: () => import("@/views/fueling/FuelingScanQr.vue"),
	},
	{
		path: "/dashboard/fueling/unit/:unitId",
		name: "FuelingForm",
		component: () => import("@/views/fueling/Form.vue"),
		props: true, // Tambahkan ini
	},
	{
		path: "/attendance",
		name: "Attendance",
		component: () => import("@/views/Attendance.vue"),
	},
	{
		name: "SuratTugasDetailView",
		path: "/surat-tugas-requests",
		component: () => import("@/views/SuratTugas.vue"),
	},
	{
		path: "/login",
		name: "Login",
		component: () => import("@/views/Login.vue"),
	},
	{
		path: "/profile",
		name: "Profile",
		component: () => import("@/views/Profile.vue"),
	},
	{
		path: "/notifications",
		name: "Notifications",
		component: () => import("@/views/Notifications.vue"),
	},
	{
		path: "/settings",
		name: "Settings",
		component: () => import("@/views/AppSettings.vue"),
	},
	{
		path: "/invalid-employee",
		name: "InvalidEmployee",
		component: () => import("@/views/InvalidEmployee.vue"),
	},
	...attendanceRoutes,
	...claimRoutes,
	...employeeAdvanceRoutes,
]

const router = createRouter({
	history: createWebHistory("/mobile"),
	routes,
})

export default router
