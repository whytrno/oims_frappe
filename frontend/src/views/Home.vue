<template>
	<BaseLayout>
		<template #body>
			<div class="flex flex-col items-center my-7 p-4 gap-7">
				<CheckInPanel />
				<QuickLinks :items="quickLinks" :title="__('Quick Links')" />
				<!-- <RequestPanel /> -->
			</div>
		</template>
	</BaseLayout>
</template>

<script setup>
import { inject, markRaw } from "vue"

import CheckInPanel from "@/components/CheckInPanel.vue"
import QuickLinks from "@/components/QuickLinks.vue"
import BaseLayout from "@/components/BaseLayout.vue"
import ExpenseIcon from "@/components/icons/ExpenseIcon.vue"

const __ = inject("$translate")

const quickLinks = [
	{
		icon: markRaw(ExpenseIcon),
		title: __("Claim an Expense"),
		route: "ExpenseClaimFormView",
	},
]
</script>
