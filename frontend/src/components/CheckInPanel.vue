<template>
	<div class="flex flex-col bg-white rounded w-full py-6 px-4 border-none">
		<h2 class="text-lg font-bold text-gray-900">Hey, {{ employee?.data?.nama_lengkap }} 👋</h2>

		<div class="font-medium text-sm text-gray-500 mt-1.5" v-if="lastLog">
			Last {{ lastLogType }} was at {{ lastLogTime }}
		</div>
		<div class="font-medium text-sm text-gray-500 mt-1.5" v-else>
			Anda belum absen hari ini
		</div>

		<router-link
			class="mt-4 mb-1 drop-shadow-sm text-base"
			:to="{ name: 'Attendance' }"
		>
			<Button class="w-full py-5">
				<template #prefix>
				<FeatherIcon
					:name="nextAction.action === 'In' ? 'arrow-right-circle' : 'arrow-left-circle'"
					class="w-4"
				/>
				</template>
				{{ nextAction.label }}
			</Button>
		</router-link>


	</div>
</template>

<script setup>
import { createListResource, FeatherIcon } from "frappe-ui"
import { computed, inject, ref, onMounted, onBeforeUnmount} from "vue"

const DOCTYPE = "Absensi"

const socket = inject("$socket")
const employee = inject("$employee")
const dayjs = inject("$dayjs")

const checkins = createListResource({
	doctype: DOCTYPE,
	fields: ["*"],
	filters: {
		karyawan: employee.data.nrp,
	},
	orderBy: "waktu_absen desc",
})

checkins.reload()

const lastLog = computed(() => {
	if (checkins.list.loading || !checkins.data) return {}
	return checkins.data[0]
})

const lastLogType = computed(() => {
	return lastLog?.value?.tipe === "In" ? "check-in" : "check-out"
})

const nextAction = computed(() => {
	return lastLog?.value?.tipe === "In"
		? { action: "Out", label: "Check Out" }
		: { action: "In", label: "Check In" }
})

const lastLogTime = computed(() => {
	const timestamp = lastLog?.value?.waktu_absen
	const formattedTime = dayjs(timestamp).format("hh:mm a")

	if (dayjs(timestamp).isToday()) return formattedTime
	else if (dayjs(timestamp).isYesterday()) return `${formattedTime} yesterday`
	else if (dayjs(timestamp).isSame(dayjs(), "year"))
		return `${formattedTime} on ${dayjs(timestamp).format("D MMM")}`

	return `${formattedTime} on ${dayjs(timestamp).format("D MMM, YYYY")}`
})

onMounted(() => {
	socket.emit("doctype_subscribe", DOCTYPE)
	socket.on("list_update", (data) => {
		if (data.doctype == DOCTYPE) {
			checkins.reload()
		}
	})
})

onBeforeUnmount(() => {
	socket.emit("doctype_unsubscribe", DOCTYPE)
	socket.off("list_update")
})

</script>
