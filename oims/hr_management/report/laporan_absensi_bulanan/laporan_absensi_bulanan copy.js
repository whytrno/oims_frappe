// Copyright (c) 2024, Wahyu Triono and contributors
// For license information, please see license.txt

frappe.query_reports["Laporan Absensi Bulanan"] = {
	filters: [
		{
			fieldname: "month",
			label: __("Month"),
			fieldtype: "Select",
			reqd: 1,
			options: [
				{ value: 1, label: __("Jan") },
				{ value: 2, label: __("Feb") },
				{ value: 3, label: __("Mar") },
				{ value: 4, label: __("Apr") },
				{ value: 5, label: __("May") },
				{ value: 6, label: __("June") },
				{ value: 7, label: __("July") },
				{ value: 8, label: __("Aug") },
				{ value: 9, label: __("Sep") },
				{ value: 10, label: __("Oct") },
				{ value: 11, label: __("Nov") },
				{ value: 12, label: __("Dec") },
			],
			default: frappe.datetime.str_to_obj(frappe.datetime.get_today()).getMonth() + 1,
		},
		{
			fieldname: "year",
			label: __("Year"),
			fieldtype: "Select",
			reqd: 1,
		},
		{
			fieldname: "site",
			label: __("Lokasi Absen"),
			fieldtype: "Link",
			options: "Lokasi Absen",
		},
		{
			fieldname: "jenis",
			label: __("Jenis"),
			fieldtype: "Select",
			options: [
				{ value: "Perbulan", label: __("Perbulan") },
				{ value: "Minggu ke 1", label: __("Minggu 1 (1 - 7)") },
				{ value: "Minggu ke 2", label: __("Minggu 2 (8 - 14)") },
				{ value: "Minggu ke 3", label: __("Minggu 3 (15 - 21)") },
				{ value: "Minggu ke 4", label: __("Minggu 4 (22 - 28)") },
				{ value: "Minggu ke 5", label: __("Minggu 5 (29 - 35)") },
			],
		},
	],
	onload: function () {
		return frappe.call({
			method: "oims.hr_management.report.laporan_absensi_bulanan.laporan_absensi_bulanan.get_attendance_years",
			callback: function (r) {
				var year_filter = frappe.query_report.get_filter("year");
				year_filter.df.options = r.message;
				year_filter.df.default = r.message.split("\n")[0];
				year_filter.refresh();
				year_filter.set_input(year_filter.df.default);
			},
		});
	},
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		return value;
	},
};
