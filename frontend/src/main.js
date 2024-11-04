import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { initSocket } from "./socket";
import {
	Button,
	Input,
	setConfig,
	frappeRequest,
	resourcesPlugin,
	FormControl,
} from "frappe-ui";
import EmptyState from "@/components/EmptyState.vue";
import { IonicVue } from "@ionic/vue";
import { session } from "@/data/session";
import { userResource } from "@/data/user";
import { employeeResource } from "@/data/employee";
import dayjs from "@/utils/dayjs";
import getIonicConfig from "@/utils/ionicConfig";

import FirebasePushNotification from "../public/firebase-push-notification";

import "@ionic/vue/css/core.css";
import "./theme/variables.css";
import "./main.css";

const app = createApp(App);
const socket = initSocket();

setConfig("resourceFetcher", frappeRequest);
app.use(resourcesPlugin);

app.component("Button", Button);
app.component("Input", Input);
app.component("FormControl", FormControl);
app.component("EmptyState", EmptyState);

app.use(router);
app.use(IonicVue, getIonicConfig());

if (session?.isLoggedIn && !employeeResource?.data) {
	employeeResource.reload();
}

app.provide("$session", session);
app.provide("$user", userResource);
app.provide("$employee", employeeResource);
app.provide("$socket", socket);
app.provide("$dayjs", dayjs);

const registerFirebasePushNotification = async () => {
	const firebaseConfig = {
		apiKey: "AIzaSyAhGh-vOPx0jMQ1E3qDvLaBMJkWi8_9nQw",
		authDomain: "oims-orecon.firebaseapp.com",
		projectId: "oims-orecon",
		storageBucket: "oims-orecon.firebasestorage.app",
		messagingSenderId: "348022824949",
		appId: "1:348022824949:web:252cf9a2a4e1744141cabc",
		measurementId: "G-YFSDPMP2DZ",
		vapidKey: "BJHZXMRHJYh74X0HSOvGK7VLWGd2hQaKL_hvm6pn8xiRBt8Yk6Qv7roP1-DXCc3jIEp8rZ3xa_dNHbmEFA3Wc0c" // Add your VAPID key here if needed
	};

	window.firebasePushNotification = new FirebasePushNotification(firebaseConfig);

	// Call initialize to request permission and get the token
	await window.firebasePushNotification.initialize();

	if ("serviceWorker" in navigator) {
		let serviceWorkerURL = "/assets/oims/frontend/sw.js";

		try {
			serviceWorkerURL = `${serviceWorkerURL}?config=${encodeURIComponent(
				firebaseConfig
			)}`;
		} catch (err) {
			console.error("Failed to fetch FCM config", err);
		}

		navigator.serviceWorker
			.register("/assets/oims/frontend/firebase-messaging-sw.js")
			.then((registration) => {
				// Initialize messaging with the service worker registration
				window.firebasePushNotification.initialize(registration).then(() => {
					console.log("Firebase Push Notification initialized");
				});
			})
			.catch((err) => {
				console.error("Failed to register service worker", err);
			});
	} else {
		console.error("Service worker not enabled/supported by the browser");
	}
};


router.isReady().then(async () => {
	if (!window.frappe) window.frappe = {};
	registerFirebasePushNotification();
	app.mount("#app");
});

router.beforeEach(async (to, _, next) => {
	let isLoggedIn = session.isLoggedIn;

	try {
		if (isLoggedIn) await userResource.reload();
	} catch (error) {
		isLoggedIn = false;
	}

	if (!isLoggedIn) {
		if (to.path === "/update-password") {
			return next(false);
		} else if (to.name !== "Login") {
			next({ name: "Login" });
		}
	}

	if (isLoggedIn && to.name !== "InvalidEmployee") {
		await employeeResource.promise;
		if (
			!employeeResource?.data ||
			employeeResource?.data?.user_id !== userResource.data.name
		) {
			next({ name: "InvalidEmployee" });
		} else if (to.name === "Login") {
			next({ name: "Home" });
		} else {
			next();
		}
	} else {
		next();
	}
});
