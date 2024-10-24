frappe.ready(function() {
	frappe.web_form.after_load = function() {
		console.log("web form loaded");
		// frappe.web_form.set_value('job_title', 'Software Developer');	
	}
})