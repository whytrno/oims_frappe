<template>
	<ion-page>
		<ion-content :fullscreen="true">
			<FormView v-if="formFields.length > 0" doctype="Fueling Table" v-model="fuelingData" :isSubmittable="true"
				:fields="formFieldsWithStaticFields" @validateForm="validateForm" />
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent, loadingController } from "@ionic/vue";
import { createResource, FeatherIcon } from "frappe-ui";
import { inject, ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router"
import FormView from "@/components/FormView.vue";

const employee = inject("$employee")

const router = useRouter();
const user = inject("$user");
const formFields = ref([]);
const shift = ref([]);
const fuelingData = ref([]);

const props = defineProps({
	unitId: {
		type: String,
		required: true,
	},
});

const formFieldsWithStaticFields = computed(() => [
	{
		label: "Tanggal Shift",
		fieldname: "tanggal_shift",
		fieldtype: "Data",
		read_only: 1,
		default: shift.value.tanggal_shift || "",
	},
	{
		label: "Unit",
		fieldname: "unit",
		fieldtype: "Data",
		read_only: 1,
		default: shift.value.unit || "",
	},
	{
		label: "Jenis Operator",
		fieldname: "jenis_operator",
		fieldtype: "Data",
		read_only: 1,
		default: shift.value.jenis_operator || "",
	},
	{
		label: "Nama Operator",
		fieldname: "nama_operator",
		fieldtype: "Data",
		read_only: 1,
		default: shift.value.operator || "",
	},
	{
		label: "Pengisi Bahan Bakar",
		fieldname: "nama_pengisi_bahan_bakar",
		fieldtype: "Data",
		read_only: 1,
		default: user.data?.full_name || "",
	},
	{
		label: "Waktu Pengisian",
		fieldname: "waktu",
		fieldtype: "Datetime",
		read_only: 0,
		reqd: 1,
	},
	// {
	// 	label: "Sisa Jatah Fuel (Liter)",
	// 	fieldname: "sisa_jatah_fuel",
	// 	fieldtype: "Data",
	// 	read_only: 1,
	// 	default: 200,
	// },
	...formFields.value, // Merge dynamic form fields fetched from API
]);

onMounted(async () => {
	const loading = await loadingController.create({
		message: 'Check apakah unit ada pada shift hari ini...',
	});
	loading.present();

	try {
		// Fetch shift data
		const shiftResponse = createResource({
			url: "minning_production.api.get_shift_by_unit_today",
			params: { unit: props.unitId },
			transform(data) {
				return {
					tanggal_shift: `${data.tanggal_shift} | ${data.tipe_shift}`,
					...data,
				};
			},
		});
		await shiftResponse.fetch();
		shift.value = shiftResponse.data;

		// Fetch form fields
		const fieldsResponse = createResource({
			url: "oims.api.get_doctype_fields",
			params: { doctype: "Fueling Table" },
			transform(data) {
				const excludeFields = ["pengisi_bahan_bakar", "waktu"];
				return data.filter((field) => !excludeFields.includes(field.fieldname));
			},
		});
		await fieldsResponse.fetch();
		formFields.value = fieldsResponse.data;

		fuelingData.value = {
			nama_pengisi_bahan_bakar: user.data.full_name,
			pengisi_bahan_bakar: employee.data.name,
			volume_litter: null,
			hm: null,
			shift: shift.value.tanggal_shift,
			parent: shift.value.name,
			waktu: null,
			parenttype: "Shift", // Nama Parent Doctype
			parentfield: "refueling_data",
		};

		formFieldsWithStaticFields.value = computed(() => [
			{
				label: "Tanggal Shift",
				fieldname: "tanggal_shift",
				fieldtype: "Data",
				read_only: 1,
				default: shift.data?.shift
			},
			{
				label: "Unit",
				fieldname: "unit",
				fieldtype: "Data",
				read_only: 1,
				default: shift.data?.unit
			},
			{
				label: "Jenis Operator",
				fieldname: "jenis_operator",
				fieldtype: "Data",
				read_only: 1,
				default: shift.data?.jenis_operator,
			},
			{
				label: "Nama Operator",
				fieldname: "nama_operator",
				fieldtype: "Data",
				read_only: 1,
				default: shift.data?.operator
			},
			{
				label: "Pengisi Bahan Bakar",
				fieldname: "nama_pengisi_bahan_bakar",
				fieldtype: "Data",
				read_only: 1,
				default: user.data.full_name
			},
			// {
			// 	label: "Waktu Pengisian",
			// 	fieldname: "waktu",
			// 	fieldtype: "Datetime",
			// 	read_only: 0,
			// 	reqd: 1,
			// 	default: new Date().toISOString(),
			// },
			// {
			// 	label: "Sisa Jatah Fuel (Liter)",
			// 	fieldname: "sisa_jatah_fuel",
			// 	fieldtype: "Data",
			// 	read_only: 1,
			// 	default: 200
			// },
			...formFields.value,
		])

		loading.dismiss();
	} catch (error) {
		console.error("Error loading data:", error);
	} finally {
		loading.dismiss();
	}
});

// Function to validate and submit the form
function validateForm() {
	// Custom validation logic, if needed
	if (!fuelingData.value.volume_litter || !fuelingData.value.hm || !fuelingData.value.waktu) {
		alert("Please fill in the required fields.");
		return false;
	}
	// Additional submit actions here if needed
	return true;
}
</script>
