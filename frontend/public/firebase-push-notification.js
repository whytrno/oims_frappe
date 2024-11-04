import { initializeApp } from "firebase/app";
import {
    getMessaging,
    getToken,
    onMessage,
    isSupported,
    deleteToken,
} from "firebase/messaging";

class FirebasePushNotification {
    constructor(config) {
        // Initialize Firebase App only once
        if (!FirebasePushNotification.instance) {
            this.app = initializeApp(config);
            this.messaging = getMessaging(this.app);
            FirebasePushNotification.instance = this; // Singleton pattern
        } else {
            return FirebasePushNotification.instance;
        }

        this.config = config;
        this.token = null;
        this.onMessageCallback = null;
    }

    // Initialize Firebase App and Messaging
    async initialize() {
        if (!(await isSupported())) {
            console.warn("FCM is not supported on this device.");
            return;
        }

        // Request permission and get token
        try {
            const permission = await Notification.requestPermission();
            if (permission === "granted") {
                await this.getFCMToken();
                console.log("Push notifications enabled.");
            } else {
                console.warn("Notification permission not granted.");
            }
        } catch (error) {
            console.error("Failed to get notification permission:", error);
        }
    }

    // Get FCM token
    async getFCMToken() {
        try {
            this.token = await getToken(this.messaging, { vapidKey: this.config.vapidKey });
            localStorage.setItem("firebase_token", this.token);
			alert(this.token);
        } catch (error) {
            console.error("Failed to get FCM token:", error);
        }
    }

    // Delete FCM token
    async deleteFCMToken() {
        try {
            await deleteToken(this.messaging);
            localStorage.removeItem("firebase_token");
            console.log("FCM token deleted.");
        } catch (error) {
            console.error("Failed to delete FCM token:", error);
        }
    }

    // Listen for incoming messages
    onMessage(callback) {
        if (!this.messaging) {
            console.warn("Firebase messaging is not initialized.");
            return;
        }
        this.onMessageCallback = callback;
        onMessage(this.messaging, (payload) => {
            // console.log("Message received:", payload);
            if (this.onMessageCallback) this.onMessageCallback(payload);
        });
    }
}

export default FirebasePushNotification;
