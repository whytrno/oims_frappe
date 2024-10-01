frappe.provide('frappe.desktop');

frappe.call('frappe.desk.desktop.get_workspace_sidebar_items')
	.then(r => {
		if (r.message && r.message.pages) {
			frappe.desktop.add_sidebar_item({
				label: __("Your Custom App"),
				icon: 'octicon octicon-project', // Atau gunakan path ke logo custom Anda
				route: '#custom-app',
				type: 'module',
				idx: r.message.pages.length + 1 // Menempatkan item di akhir list
			});
		}
	});
