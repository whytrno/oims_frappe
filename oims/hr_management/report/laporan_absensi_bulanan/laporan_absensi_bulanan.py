# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

from calendar import monthrange
from itertools import groupby

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Extract, Sum
from frappe.utils import cint, cstr, getdate
from frappe.utils.nestedset import get_descendants_of


Filters = frappe._dict

status_map = {
	"Hadir": "H",
	# "Tidak Hadir": "TH",
	"Izin": "I",
	"Work From Home": "WFH",
}

day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def execute(filters: Filters | None = None):
	if not (filters.month and filters.year):
		filters.month, filters.year = getdate().month, getdate().year

	attendance_map = get_attendance_map(filters)
	if not attendance_map:
		frappe.msgprint(_("No attendance records found."), alert=True, indicator="orange")
		return [], [], None, None

	columns = get_columns(filters)
	data = get_data(filters)

	if not data:
		frappe.msgprint(_("No attendance records found for this criteria."), alert=True, indicator="orange")
		return columns, [], None, None

	message = get_message() if not filters.summarized_view else ""
	chart = get_chart_data(attendance_map, filters)

	return columns, data, message, chart

def get_attendance_map(filters):
	attendance_records = frappe.get_all(
		"Absensi",
		filters={
			"waktu_absen": ["between", (f"{filters.year}-{filters.month}-01", f"{filters.year}-{filters.month}-{monthrange(filters.year, filters.month)[1]}")]
		},
		fields=["site", "karyawan", "tipe", "waktu_absen", "ambil_jatah_makan"]
	)

	attendance_map = {}

	for record in attendance_records:
		karyawan = record.karyawan
		karyawan_doc = frappe.get_doc("Karyawan", karyawan)
		nama_lengkap = karyawan_doc.nama_lengkap
		ambil_jatah_makan = record.ambil_jatah_makan
		site = record.site
		tipe = record.tipe
		# Ambil hanya hari dari waktu_absen (contoh: 29)
		hari_absen = record.waktu_absen.day

		# Jika nama_lengkap belum ada di attendance_map, tambahkan
		if karyawan not in attendance_map:
			attendance_map[karyawan] = {}

		# Jika site belum ada untuk nama_karyawan, tambahkan
		if site not in attendance_map[karyawan]:
			attendance_map[karyawan][site] = {}

		# Tambahkan hari dan tipe absen ke dalam map

		attendance_map[karyawan][site][hari_absen] = tipe
		attendance_map[karyawan][site]["nama_karyawan"] = nama_lengkap
		attendance_map[karyawan][site]["ambil_jatah_makan"] = ambil_jatah_makan

	return attendance_map


def get_message() -> str:
	message = ""
	colors = ["green", "red", "orange", "green", "#318AD8", "", ""]

	count = 0
	for status, abbr in status_map.items():
		message += f"""
			<span style='border-left: 2px solid {colors[count]}; padding-right: 12px; padding-left: 5px; margin-right: 3px;'>
				{status} - {abbr}
			</span>
		"""
		count += 1

	return message

def get_columns(filters: Filters) -> list[dict]:
	columns = []

	if filters.group_by:
		options_mapping = {
			"Branch": "Branch",
			"Grade": "Employee Grade",
			"Department": "Department",
			"Designation": "Designation",
		}
		options = options_mapping.get(filters.group_by)
		columns.append(
			{
				"label": _(filters.group_by),
				"fieldname": frappe.scrub(filters.group_by),
				"fieldtype": "Link",
				"options": options,
				"width": 120,
			}
		)

	columns.extend(
		[
			{
				"label": _("NRP"),
				"fieldname": "nrp",
				"fieldtype": "Link",
				"options": "Karyawan",
				"width": 120,
			},
			{"label": _("Nama karyawan"), "fieldname": "nama_karyawan", "fieldtype": "Data", "width": 150},
			{
				"label": _("Site"),
				"fieldname": "site",
				"fieldtype": "Link",
				"options": "Lokasi Site",
				"width": 70,
			},
		]
	)

	columns.extend(get_columns_for_days(filters))

	return columns

def get_columns_for_days(filters: Filters) -> list[dict]:
	total_days = get_total_days_in_month(filters)
	days = []

	for day in range(1, total_days + 1):
		day = cstr(day)
		# forms the dates from selected year and month from filters
		date = f"{cstr(filters.year)}-{cstr(filters.month)}-{day}"
		# gets abbr from weekday number
		weekday = day_abbr[getdate(date).weekday()]
		# sets days as 1 Mon, 2 Tue, 3 Wed
		label = f"{day} {weekday}"
		days.append({"label": label, "fieldtype": "Data", "fieldname": day, "width": 80})

	return days

def get_total_days_in_month(filters: Filters) -> int:
	return monthrange(cint(filters.year), cint(filters.month))[1]


def get_data(filters) -> list[list]:
	total_days = get_total_days_in_month(filters)
	data = []

	# Misalkan attendance_map adalah hasil dari get_attendance_map(filters)
	attendance_map = get_attendance_map(filters)
	print(attendance_map)

	# Iterasi melalui semua karyawan dalam attendance_map
	for karyawan, site_data in attendance_map.items():
		for site, attendance in site_data.items():
			nama_lengkap_karyawan = attendance["nama_karyawan"]
			# Setiap row dimulai dengan nama karyawan dan site
			row = [karyawan, nama_lengkap_karyawan, site]

			# Untuk setiap hari dalam bulan, tambahkan "P" jika karyawan hadir, atau "A" jika absen
			for day in range(1, total_days + 1):
				# Jika ada data absensi untuk hari tersebut, gunakan status absensi (misalnya "Present" atau "Absent")
				if day in attendance:
					if attendance[day] == "In" or attendance[day] == "Out":
						row.append("H")
					elif attendance[day] == "Izin":
						row.append("I")
					else:
						# Jika tidak ada data untuk hari itu, anggap absen (A)
						row.append(" ")
				else:
					row.append(" ")

			data.append(row)

	return data

def get_chart_data(attendance_map: dict, filters: Filters) -> dict:
	days = get_columns_for_days(filters)
	labels = []
	izin = []
	hadir = []
	ambil_jatah_makan = []

	for day in days:
		date = day['label'].split(' ')[0]
		labels.append(date)
		total_hadir_on_day = total_izin_on_day = total_ambil_jatah_makan = 0

		for __, attendance_dict in attendance_map.items():
			for __, attendance in attendance_dict.items():
				print(attendance)
				attendance_on_day = attendance.get(cint(day["fieldname"]))

				if attendance_on_day == "Izin":
					total_izin_on_day += 1
				elif attendance_on_day in ["In", "Work From Home"]:
					total_hadir_on_day += 1
	
					ambil_jatah_makan_on_day = attendance.get("ambil_jatah_makan")
					if ambil_jatah_makan_on_day:
						total_ambil_jatah_makan += 1

		izin.append(total_izin_on_day)
		hadir.append(total_hadir_on_day)
		ambil_jatah_makan.append(total_ambil_jatah_makan)

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": "Izin", "values": izin},
				{"name": "Hadir", "values": hadir},
				{"name": "Ambil Jatah Makan", "values": ambil_jatah_makan},
			],
		},
		"type": "line",
		"colors": ["red", "green", "purple"],
	}
