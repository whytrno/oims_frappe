<template>
	<!-- <router-link :to="{ name: 'Attendance' }" v-slot="{ navigate }"> -->
		<ListItem class="p-3.5 bg-white rounded">
			<template #left>
				<div class="flex flex-col items-start gap-1.5">
					<!-- Parent data (dynamic) -->
					<div class="text-base font-normal text-gray-800">
						{{ item.nama_karyawan }}
					</div>
				</div>
			</template>
		</ListItem>
	<!-- </router-link> -->
</template>

<script setup>
import ListItem from "@/components/ListItem.vue"

// Terima item dari prop
const props = defineProps({
	item: {
		type: Object,
		required: true,
	},
});
</script>
