<template>
	<ion-page>
		<ion-content class="ion-no-padding">
			<div class="flex flex-col h-full w-screen sm:w-96 justify-between relative">
				<header class="bg-white shadow-sm py-4 px-3">
					<div class="flex flex-row items-center">
						<Button variant="ghost" class="!pl-0 hover:bg-white" @click="router.back()">
							<FeatherIcon name="chevron-left" class="h-5 w-5" />
						</Button>
						<h2 class="text-xl font-semibold text-gray-900">Attendance</h2>
					</div>
				</header>
				<div id="map" class="relative flex-grow">
					<div class="flex justify-between items-end my-5 mx-2 absolute bottom-0 left-0 z-[9999]">
						<div v-if="!photoTaken" class="h-1/3 w-1/3">
							<video ref="videoElement" class="h-full w-full" autoplay playsinline></video>
						</div>
						<div v-else class="h-1/3 w-1/3">
							<img :src="photoPreviewUrl" alt="Captured photo" class="h-full w-full object-cover" />
						</div>
						<button
							class="bg-blue-500 h-14 w-14 flex justify-center items-center rounded-lg hover:bg-blue-600"
							@click="photoTaken ? retakePhoto() : capturePhoto()">
							<FeatherIcon :name="photoTaken ? 'refresh-cw' : 'camera'" class="h-5 w-5 text-white" />
						</button>
					</div>
					<canvas ref="canvasElement" style="display: none;"></canvas>
				</div>
				<div class="px-5 pt-5 space-y-2">
					<div class="flex justify-between">
						<p>Status Foto</p>
						<p :class="photoTaken ? 'text-green-500' : 'text-red-500'">
							{{ photoTaken ? 'Sudah diambil' : 'Belum diambil' }}
						</p>
					</div>

					<div class="flex justify-between">
						<p>Radius Absen</p>
						<p>{{ selectedSite ? `${selectedSite.radius} m` : '- m' }}</p>
					</div>

					<div class="-my-2">
						<ion-select v-model="selectedSite" label="Lokasi Site" label-placement="fixed"
							placeholder="Pilih Lokasi Site">
							<ion-select-option v-for="lokasi in lokasiSite.data" :key="lokasi.name" :value="lokasi">
								{{ lokasi.name }}
							</ion-select-option>
						</ion-select>
					</div>

					<ion-checkbox justify="space-between" v-model="ambilJatahMakan"
						v-if="selectedSite && selectedSite.name === 'HO - HO'">Ambil Jatah Makan</ion-checkbox>
				</div>

				<div class="p-5 flex gap-5">
					<Button :variant="'solid'" :loading="loading" :loadingText="'Processing...'" class="w-full py-6 text-sm" @click="submitLog(nextAction.action)"
						:disabled="isButtonDisabled">
						{{ nextAction.label }}
					</Button>

					<Button :loading="loading" :loadingText="'Processing...'" :variant="'solid'" class="w-full py-6 text-sm" :disabled="isButtonDisabled">
						Izin
					</Button>
				</div>
			</div>
		</ion-content>
	</ion-page>
</template>

<script setup>
import { IonPage, IonContent, IonSelect, IonCheckbox, IonList, IonSelectOption, IonItem, IonSpinner } from "@ionic/vue"
import { useRouter } from "vue-router"
import { createListResource, toast, FeatherIcon, createResource } from "frappe-ui"
import { computed, inject, ref, watch, onMounted, onBeforeUnmount } from "vue"
import { modalController } from "@ionic/vue"
import L from "leaflet";
import "../../public/leaflet.css";

const router = useRouter()

const DOCTYPE = "Absensi"

const socket = inject("$socket")
const employee = inject("$employee")
const dayjs = inject("$dayjs")
const checkinTimestamp = ref(null)
const latitude = ref(0)
const longitude = ref(0)
const locationStatus = ref("")
const ambilJatahMakan = ref(true)
let map = null;
let marker = null;
let circle = null;
let cameraStream = null;
let watchID = null;

const videoElement = ref(null);
const canvasElement = ref(null);

const photoTaken = ref(false);
const photoBlob = ref(null);
const photoPreviewUrl = ref('');

const loading = ref(false);
const isButtonDisabled = ref(false);

const selectedSite = ref(null);
const checkins = createListResource({
	doctype: DOCTYPE,
	fields: ["*"],
	filters: {
		karyawan: employee.data.name,
		waktu_absen: ['>=', dayjs().startOf('day').format("YYYY-MM-DD HH:mm:ss")],
	},
	orderBy: "waktu_absen desc",
})

const lokasiSite = createListResource({
	doctype: "Lokasi Absen",
	fields: ["*"],
	filters: {
		latitude: ['is', 'set'],
		longitude: ['is', 'set']
	},
})

checkins.reload()
lokasiSite.reload()
watch(() => selectedSite.value, (newValue, oldValue) => {
	console.log("Selected Site Changed", newValue, oldValue)
})

const lastLog = computed(() => {
	if (checkins.list.loading || !checkins.data) return {}
	return checkins.data[0]
})

const nextAction = computed(() => {
	return lastLog?.value?.tipe === "In"
		? { action: "Out", label: "Check Out" }
		: { action: "In", label: "Check In" }
})

function handleLocationSuccess(position) {
	latitude.value = position.coords.latitude
	longitude.value = position.coords.longitude

	locationStatus.value = `
		Latitude: ${Number(latitude.value).toFixed(5)}°,
		Longitude: ${Number(longitude.value).toFixed(5)}°
		`

	if (marker) {
		const newLatLng = L.latLng(latitude.value, longitude.value);
		marker.setLatLng(newLatLng);
		// map.setView(newLatLng, 17);
	}
}

const startWatchingPosition = () => {
	if (navigator.geolocation) {
		watchID = navigator.geolocation.watchPosition(
			handleLocationSuccess,
			handleLocationError,
			{
				enableHighAccuracy: true,
				timeout: 1000,
				maximumAge: 0 // Optional: do not use cached location
			}
		);
	} else {
		locationStatus.value = "Geolocation is not supported by your current browser"
	}
};

const stopWatchingPosition = () => {
	if (watchID !== null) {
		navigator.geolocation.clearWatch(watchID);
		watchID = null;
	}
};

function handleLocationError(error) {
	locationStatus.value = "Unable to retrieve your location"
	if (error) locationStatus.value += `: ERROR(${error.code}): ${error.message}`
}

const fetchLocation = () => {
	if (!navigator.geolocation) {
		locationStatus.value = "Geolocation is not supported by your current browser"
	} else {
		navigator.geolocation.getCurrentPosition(handleLocationSuccess, handleLocationError)
	}
}

const handleEmployeeCheckin = () => {
	checkinTimestamp.value = dayjs().format("YYYY-MM-DD HH:mm:ss")
	fetchLocation()
}

const capturePhoto = () => {
	if (!videoElement.value || !canvasElement.value) {
		console.error('Video or canvas element not found');
		return;
	}

	const video = videoElement.value;
	const canvas = canvasElement.value;
	const context = canvas.getContext('2d');

	if (!context) {
		console.error('Unable to get 2D context from canvas');
		return;
	}

	// Set canvas dimensions to match video
	canvas.width = video.videoWidth;
	canvas.height = video.videoHeight;

	// Draw current video frame on canvas
	context.drawImage(video, 0, 0, canvas.width, canvas.height);

	// Convert canvas to blob
	canvas.toBlob((blob) => {
		photoBlob.value = blob;
		photoTaken.value = true;
		photoPreviewUrl.value = URL.createObjectURL(blob);
		toast({
			title: "Photo Captured",
			text: "Photo has been successfully captured.",
			icon: "check-circle",
			position: "top-center",
			iconClasses: "text-green-500",
		});
	}, 'image/jpeg');
};

const retakePhoto = () => {
	photoTaken.value = false;
	photoBlob.value = null;
	photoPreviewUrl.value = '';
	initializeCamera();
};

const uploadPhoto = async () => {
	if (!photoBlob.value) return null;

	const formData = new FormData();
	const today = dayjs();
	const year = today.format('YYYY');
	const month = today.format('MM');
	const day = today.format('DD');

	const folderPath = `absensi/${year}/${month}/${day}`;
	const folderStructure = folderPath.split('/').filter(Boolean);

	let currentPath = 'Home';
	const createdFolders = []; // Menyimpan URL folder yang berhasil dibuat

	for (const folder of folderStructure) {
		currentPath += `/${folder}`;

		try {
			const data = await createListResource({
				doctype: "File",
			}).insert.submit(
				{
					"doctype": "File",
					"file_name": folder,
					"folder": currentPath.split('/').slice(0, -1).join('/'),
					"is_folder": 1,
					"is_private": 1
				}
			);

			if (data && data.message && data.message.file_url) {
				createdFolders.push(data.message.file_url);
			} else {
				console.error(`Error: Invalid response structure for folder ${currentPath}:`, data);
			}
		} catch (error) {
			console.error(`Error creating folder ${currentPath}:`, error);
		}

		// Menambahkan delay setelah setiap pembuatan folder
		// await new Promise(resolve => setTimeout(resolve, 2000));
	}

	formData.append('file', photoBlob.value, `${employee.data.nama_lengkap}.jpg`);
	formData.append('folder', `Home/${folderPath}`);

	try {
		const response = await fetch('/api/method/upload_file', {
			method: 'POST',
			body: formData,
		});
		const result = await response.json();
		return result.message.file_url;
	} catch (error) {
		console.error('Error uploading photo:', error);
		return null;
	}
};

const getDistanceFromLatLonInMeters = (lat1, lon1, lat2, lon2) => {
	const R = 6371e3; // Radius of the earth in meters
	const dLat = (lat2 - lat1) * Math.PI / 180;
	const dLon = (lon2 - lon1) * Math.PI / 180;

	const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
		Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
		Math.sin(dLon / 2) * Math.sin(dLon / 2);
	const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

	return R * c; // Distance in meters
};

const submitLog = async (logType) => {
	loading.value = true;
	isButtonDisabled.value = true; // Disable the button
	const action = logType === "In" ? "In" : "Out";

	// Check if a site is selected
	if (!selectedSite.value) {
		toast({
			title: "Error",
			text: "Please select a site location.",
			icon: "alert-circle",
			position: "top-center",
			iconClasses: "text-red-500",
		});
		return;
	}

	// Check if a photo has been taken
	if (!photoTaken.value) {
		toast({
			title: "Error",
			text: "Please capture a photo before submitting.",
			icon: "alert-circle",
			position: "top-center",
			iconClasses: "text-red-500",
		});
		return;
	}

	// Calculate the distance from the user's location to the selected site
	const distance = getDistanceFromLatLonInMeters(
		latitude.value,
		longitude.value,
		selectedSite.value.latitude,
		selectedSite.value.longitude
	);

	// Check if the distance exceeds the selected site's radius
	if (distance > selectedSite.value.radius) {
		toast({
			title: "Error",
			text: "You are outside the allowed radius for this site.",
			icon: "alert-circle",
			position: "top-center",
			iconClasses: "text-red-500",
		});
		return;
	}

	const photoUrl = await uploadPhoto();
	if (!photoUrl) {
		toast({
			title: "Error",
			text: "Failed to upload photo. Please try again.",
			icon: "alert-circle",
			position: "top-center",
			iconClasses: "text-red-500",
		});
		return;
	}

	createResource({
		url: "oims.api.submit_attendance",
		method: "POST",
		params: {
			karyawan: employee.data.name,
			lokasi_absen: selectedSite.value.name,
			foto: photoUrl,
			tipe: logType,
			// tipe: "In",
			waktu_absen: checkinTimestamp.value,
			latitude: latitude.value,
			longitude: longitude.value,
			ambil_jatah_makan: ambilJatahMakan.value,
		},
		auto: true,
		onError(error) {
			
			toast({
				title: "Error",
				text: `${action} failed!`,
				icon: "alert-circle",
				position: "top-center",
				iconClasses: "text-red-500",
			});
			loading.value = false;
			isButtonDisabled.value = false; // Re-enable on error
		},
		onSuccess(data) {
			modalController.dismiss();
			toast({
				title: "Success",
				text: `${action} successful!`,
				icon: "check-circle",
				position: "top-center",
				iconClasses: "text-green-500",
			});
			loading.value = false;
		},
	})
};



const initializeMap = () => {
	if (map === null) {
		if (latitude.value === 0 && longitude.value === 0) {
			latitude.value = -6.3949906486826595;
			longitude.value = 106.9304776672312;
		}

		map = L.map('map').setView([latitude.value, longitude.value], 17);

		L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
			// attribution: 'Map data © OpenStreetMap contributors',
		}).addTo(map);

		marker = L.marker([latitude.value, longitude.value]).addTo(map);
	}


	setTimeout(function () {
		map.invalidateSize();
	}, 0);
}

const initializeCamera = () => {
	if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
		navigator.mediaDevices
			.getUserMedia({
				video: {
					facingMode: 'user'
				}
			})
			.then((stream) => {
				cameraStream = stream;
				if (videoElement.value) {
					videoElement.value.srcObject = stream;
				}
			})
			.catch((error) => {
				console.error('Camera access failed:', error);
			});
	}
}

watch(selectedSite, (newSite) => {
	if (newSite && map) {
		const newLatLng = L.latLng(newSite.latitude, newSite.longitude);
		map.setView(newLatLng, 17);

		// Update location status with site coordinates
		locationStatus.value = `
		Site Latitude: ${Number(newSite.latitude).toFixed(5)}°,
		Site Longitude: ${Number(newSite.longitude).toFixed(5)}°
		`;

		if (circle) {
			circle.setLatLng(newLatLng);
			circle.setRadius(newSite.radius);
		} else {
			circle = L.circle(newLatLng, {
				color: 'blue',
				fillColor: '#3498db',
				fillOpacity: 0.3,
				radius: newSite.radius
			}).addTo(map);
		}
	}
});

onMounted(() => {
	socket.emit("doctype_subscribe", DOCTYPE)
	socket.on("list_update", (data) => {
		if (data.doctype == DOCTYPE) {
			checkins.reload()
			lokasiSite.reload()
		}
	})


	// const action = router.query.action;

	handleEmployeeCheckin()
	fetchLocation()
	initializeMap();
	initializeCamera();
	startWatchingPosition();
})

onBeforeUnmount(() => {
	socket.emit("doctype_unsubscribe", DOCTYPE)
	socket.off("list_update")

	if (map) {
		map.remove()
		map = null
		marker = null
		circle = null;
	}

	stopWatchingPosition();

	if (photoPreviewUrl.value) {
		URL.revokeObjectURL(photoPreviewUrl.value);
	}

	// Stop camera stream
	if (cameraStream) {
		cameraStream.getTracks().forEach((track) => track.stop());
		cameraStream = null;
	}
})
</script>
