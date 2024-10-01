// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.ui.form.on("Lokasi Site", {
	latitude: function (frm) {
		update_geolocation(frm);
	},
	longitude: function (frm) {
		update_geolocation(frm);
	},
	radius: function (frm) {
		update_geolocation(frm);
	}
});
// -6.382687, 106.928447

let circle_layer;

function update_geolocation(frm) {
	if (frm.doc.latitude && frm.doc.longitude) {
		let latitude = frm.doc.latitude;
		let longitude = frm.doc.longitude;
		let radius = frm.doc.radius || 25;  // Default radius if not provided

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
			radius: radius      // Radius in meters
		}).addTo(frm.fields_dict.peta.map);
	}
}
