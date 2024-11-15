// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Projek", {
	refresh: function (frm) {
		if (frm.doc.latitude && frm.doc.longitude) {
			let latitude = frm.doc.latitude;
			let longitude = frm.doc.longitude;

			// Update the geolocation field (peta_site)
			frm.fields_dict.peta.map.setView([latitude, longitude], 15);

			// Remove previous circle if it exists
			if (circle_layer) {
				frm.fields_dict.peta.map.removeLayer(circle_layer);
			}

			// Create a new circle with the specified radius
			circle_layer = L.circle([latitude, longitude], {
				color: 'blue',     // Border color of the circle
				fillColor: '#blue', // Fill color of the circle
				fillOpacity: 0.2,   // Opacity of the circle fill
				radius: frm.doc.radius || 25  // Default radius if not provided
			}).addTo(frm.fields_dict.peta.map);
		}
	},
	latitude: function (frm) {
		update_geolocation(frm);
	},
	longitude: function (frm) {
		update_geolocation(frm);
	},
});

function update_geolocation(frm) {
	if (frm.doc.latitude && frm.doc.longitude) {
		let latitude = frm.doc.latitude;
		let longitude = frm.doc.longitude;

		// Update the geolocation field (peta_site)
		frm.fields_dict.peta.map.setView([latitude, longitude], 15);

		// Tambahkan pin ke lokasi yang ditentukan
		let marker = L.marker([latitude, longitude]).addTo(frm.fields_dict.peta.map);
	}
}
