frappe.provide('frappe.desktop');

frappe.call('frappe.desk.desktop.get_workspace_sidebar_items')
	.then(r => {
		if (r.message && r.message.pages) {
			frappe.desktop.add_sidebar_item({
				label: __("Oims Apps"),
				icon: 'octicon octicon-project', // Atau gunakan path ke logo custom Anda
				route: '#custom-app',
				type: 'module',
				idx: r.message.pages.length + 1 // Menempatkan item di akhir list
			});
		}
	});

	// Make sure we have a dictionary to add our custom settings
const map_settings = frappe.provide("frappe.utils.map_defaults");

// Center and zoomlevel can be copied from the URL of
// the map view at openstreetmap.org.

// New default location (middle of germany).
map_settings.center = [-2.5, 118.0]; // Pusat geografis Indonesia
map_settings.zoom = 5; // Zoom level untuk mencakup seluruh wilayah Indonesia


// Use a different map: satellite instead of streets
// Examples can be found at https://leaflet-extras.github.io/leaflet-providers/preview/
// map_settings.tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
// map_settings.attribution = "Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community";
