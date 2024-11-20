<template>
	<ListItem
		:karyawan="props.doc.karyawan"
	>
		<template #left>
			<ShiftIcon class="h-5 w-5 text-gray-500" />
			<div class="flex flex-col items-start gap-1.5">
				<div class="text-base font-normal text-gray-800">
					{{ props.doc.no_surat }}
				</div>
				<div class="text-xs font-normal text-gray-500">
					{{ tanggal_berangkat }}
				</div>
				<div class="text-xs font-normal text-gray-500">
					{{ props.doc.site }} | {{ props.doc.keperluan }}
				</div>
				<template v-for="(krywn, index) in karyawan">
				<div class="text-xs font-normal text-gray-500 flex flex-col gap-1">
						<span>
							{{ index + 1 }}. {{ krywn }}
						</span>
					</div>
				</template>
			</div>
		</template>
		<template #right>
			<FeatherIcon name="chevron-right" class="h-5 w-5 text-gray-500" />
		</template>
	</ListItem>
</template>

<script setup>
import { FeatherIcon, Badge } from "frappe-ui"
import { computed, inject } from "vue"

import ListItem from "@/components/ListItem.vue"
import ShiftIcon from "./icons/ShiftIcon.vue"

const dayjs = inject("$dayjs")
const __ = inject("$translate")
const props = defineProps({
	doc: {
		type: Object,
	},
})

const karyawan = computed(() => {
    const karyawan_raw = props.doc.karyawan_for_list_view || "";
    return karyawan_raw ? karyawan_raw.split(", ") : [];
});

const tanggal_berangkat = computed(() => {
    return dayjs(props.doc.tanggal_berangkat).format("D MMM YYYY");
});
</script>
