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
import { translationsPlugin } from "./plugins/translationsPlugin.js"
import getIonicConfig from "@/utils/ionicConfig";

// OneSignal
import OneSignalVuePlugin from '@onesignal/onesignal-vue3';

import "@ionic/vue/css/core.css";
import "./theme/variables.css";
import "./main.css";

// Create Vue app instance
const app = createApp(App);

// OneSignal configuration
app.use(OneSignalVuePlugin, {
	appId: '0e972c8f-983c-41ac-a097-837c7b92a80e',
	// appId: '57681691-1547-471a-a362-799e19617665',
	notifyButton: {
		enable: true
	},
	serviceWorkerParam: { scope: "/assets/oims/frontend/" },
	serviceWorkerPath: "/assets/oims/frontend/OneSignalSDKWorker.js",
});

const socket = initSocket();
setConfig("resourceFetcher", frappeRequest);
app.use(resourcesPlugin);
app.use(translationsPlugin)

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

router.isReady().then(async () => {
	if (!window.frappe) window.frappe = {};
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
