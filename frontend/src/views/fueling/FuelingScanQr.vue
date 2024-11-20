<template>
	<ion-page>
		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96 justify-between relative">
				<header class="bg-white shadow-sm py-4 px-3">
					<div class="flex flex-row items-center">
						<Button variant="ghost" class="!pl-0 hover:bg-white" @click="router.back()">
							<FeatherIcon name="chevron-left" class="h-5 w-5" />
						</Button>
						<h2 class="text-xl font-semibold text-gray-900">Scan QR Unit</h2>
					</div>
				</header>
				<div class="h-full flex flex-col justify-center gap-10 relative">
					<qrcode-stream :torch="torchActive" :track="paintOutline" @error="onError" @detect="onDetect"
						@camera-on="onCameraOn" :paused="paused">
						<template v-if="!torchNotSupported">
							<div class="flex w-full justify-center absolute bottom-40 left-0">
								<button @click="torchActive = !torchActive" :disabled="torchNotSupported"
									:class="`bg-${torchActive ? 'blue' : 'gray'}-500 rounded-full size-20 flex items-center justify-center`">
									<TorchLightIcon class="size-10" />
								</button>
							</div>
						</template>
					</qrcode-stream>
				</div>

				<ion-modal ref="modal" :is-open="showModal" :initial-breakpoint="1" :breakpoints="[0, 1]"
					backdropDismiss="false">
					<div class="h-120 w-full flex flex-col items-center justify-center gap-5 p-4 mb-5">
						<div class="flex flex-col gap-5 mt-2 items-center justify-center w-full">
							<div class="font-bold text-xl">
								Unit Detail
							</div>
							<div class="flex justify-center gap-5">
								<ion-img :src="unitData?.foto_unit" :alt="unitData.no_lambung"></ion-img>
							</div>
							<div class="font-medium text-gray-800 text-sm text-left w-full flex flex-col gap-3">
								<div class="flex justify-between">
									<strong>No Lambung :</strong>
									<p>{{ unitData.no_lambung }}</p>
								</div>

								<div class="flex justify-between">
									<strong>Kelas :</strong>
									<p>{{ unitData.kelas }}</p>
								</div>

								<div class="flex justify-between">
									<strong>Model :</strong>
									<p>{{ unitData.model }}</p>
								</div>
							</div>
						</div>

						<div class="flex justify-between gap-3 w-full">
							<Button @click="closeModal" variant="solid" class="w-full py-5 text-sm">
								Tutup
							</Button>
							<Button @click="goToFuelingForm" variant="solid" class="w-full py-5 text-sm" theme="blue">
								Selanjutnya
							</Button>
						</div>
					</div>
				</ion-modal>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { QrcodeStream } from 'vue-qrcode-reader';
import { createResource,FeatherIcon } from "frappe-ui";
import { ref } from "vue";
import { useRouter } from "vue-router";
import TorchLightIcon from "@/components/icons/TorchLightIcon.vue"
import { IonPage, IonContent, IonModal, toastController, IonImg, IonButton, loadingController } from "@ionic/vue"
import { onMounted, onUnmounted } from "vue";
import { onBeforeRouteLeave } from "vue-router";

const router = useRouter();
const error = ref("");
const showModal = ref(false);
const unitData = ref(null);
const torchActive = ref(false)
const torchNotSupported = ref(false)
const paused = ref(false)

function onCameraOn(capabilities) {
	torchNotSupported.value = !capabilities.torch
}

function startCamera() {
	paused.value = false; // Pause scanning
}

function stopCamera() {
	paused.value = true; // Pause scanning
}

onMounted(() => {
	paused.value = false; // Pastikan scanning dimulai
	startCamera(); // Pastikan kamera dinyalakan
});

// onUnmounted(() => {
// 	stopCamera(); // Pastikan kamera dihentikan
// });

// // Restart kamera setiap kali halaman diakses ulang
// onBeforeRouteLeave((to, from, next) => {
// 	stopCamera(); // Stop the camera before leaving the route
// 	next(); // Proceed with the route change
// });


const goToFuelingForm = async () => {
	const loading = await loadingController.create({
		message: 'Check apakah unit ada pada shift hari ini...',
	});
	loading.present();

	if (unitData.value) {
		const shift = createResource({
			url: "minning_production.api.check_there_is_shift_unit_today",
			params: {
				unit: unitData.value.no_lambung,
			},
			onError(error) {
				if (error && error.exc_type === "AuthenticationError") {
					router.push("/login");
				}
			},
		});

		try {
			await shift.fetch();

			if (shift.data) {
				loading.dismiss();
				showModal.value = false;

				router.push({
					name: "FuelingForm",
					params: {
						unitId: unitData.value.no_lambung,
					},
				});
			} else {
				loading.dismiss();
				const toast = await toastController.create({
					message: 'Unit tersebut tidak digunakan pada shift di hari ini',
					duration: 3000,
					position: 'top',
					color: 'danger',
				});

				await toast.present();
			}
		} catch (err) {
			loading.dismiss();
			console.error("Error loading unit data:", err);
		}
	}
}

const onDetect = async (result) => {
	const result_value = result[0]['rawValue'];
	paused.value = true;

	const loading = await loadingController.create({
		message: 'Mendeteksi unit...',
	});
	loading.present();

	const unit = createResource({
		url: "minning_production.api.get_unit_info",
		auto: true,
		params: {
			unit: result_value,
		},
		async onError(error) {
			if (error && error.exc_type === "AuthenticationError") {
				router.push("/login");
			}
		},
	});

	try {
		await unit.fetch();
		unitData.value = unit.data;

		loading.dismiss();
		showModal.value = true;
	} catch (err) {
		paused.value = false;
		showModal.value = false;

		const toast = await toastController.create({
			message: 'Unit tidak ditemukan',
			duration: 3000,
			position: 'top',
			color: 'danger',
		});

		await toast.present();
	}
};

function paintOutline(detectedCodes, ctx) {
	for (const detectedCode of detectedCodes) {
		const [firstPoint, ...otherPoints] = detectedCode.cornerPoints;

		ctx.strokeStyle = 'red';

		ctx.beginPath();
		ctx.moveTo(firstPoint.x, firstPoint.y);
		for (const { x, y } of otherPoints) {
			ctx.lineTo(x, y);
		}
		ctx.lineTo(firstPoint.x, firstPoint.y);
		ctx.closePath();
		ctx.stroke();
	}
}

function onError(err) {
	error.value = `[${err.name}]: `;

	if (err.name === 'NotAllowedError') {
		error.value += 'you need to grant camera access permission';
	} else if (err.name === 'NotFoundError') {
		error.value += 'no camera on this device';
	} else if (err.name === 'NotSupportedError') {
		error.value += 'secure context required (HTTPS, localhost)';
	} else if (err.name === 'NotReadableError') {
		error.value += 'is the camera already in use?';
	} else if (err.name === 'OverconstrainedError') {
		error.value += 'installed cameras are not suitable';
	} else if (err.name === 'StreamApiNotSupportedError') {
		error.value += 'Stream API is not supported in this browser';
	} else if (err.name === 'InsecureContextError') {
		error.value += 'Camera access is only permitted in secure context. Use HTTPS or localhost rather than HTTP.';
	} else {
		error.value += err.message;
	}
}

function closeModal() {
	showModal.value = false;
	paused.value = false;
}
</script>

<style scoped>
.fixed {
	position: fixed;
}

.inset-0 {
	top: 0;
	right: 0;
	bottom: 0;
	left: 0;
}

.bg-opacity-50 {
	background-color: rgba(0, 0, 0, 0.5);
}

video {
	transform: scaleX(-1);
}
</style>
