// Give the service worker access to Firebase Messaging.
// Note that you can only use Firebase Messaging here. Other Firebase libraries
// are not available in the service worker.
importScripts("https://www.gstatic.com/firebasejs/8.2.5/firebase-app.js");
importScripts("https://www.gstatic.com/firebasejs/8.2.5/firebase-messaging.js");

// Initialize the Firebase app in the service worker by passing in
// your app's Firebase config object.
// https://firebase.google.com/docs/web/setup#config-object
firebase.initializeApp({
	apiKey: "AIzaSyAhGh-vOPx0jMQ1E3qDvLaBMJkWi8_9nQw",
	authDomain: "oims-orecon.firebaseapp.com",
	projectId: "oims-orecon",
	storageBucket: "oims-orecon.firebasestorage.app",
	messagingSenderId: "348022824949",
	appId: "1:348022824949:web:252cf9a2a4e1744141cabc",
	measurementId: "G-YFSDPMP2DZ"
});

// Retrieve an instance of Firebase Messaging so that it can handle background
// messages.
const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log(
    "[firebase-messaging-sw.js] Received background message ",
    payload
  );
  // Customize notification here
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: "/firebase-logo.png",
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});
