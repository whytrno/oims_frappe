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

	message = get_message() if not get_message() else ""
	chart = get_chart_data(attendance_map, filters)

	return columns, data, message, chart

def get_attendance_map(filters):
	attendance_records = frappe.get_all(
		"Absensi",
		filters={
			"waktu_absen": ["between", (f"{filters.year}-{filters.month}-01", f"{filters.year}-{filters.month}-{monthrange(int(filters.year), int(filters.month))[1]}")]
		},
		fields=["lokasi_absen", "karyawan", "tipe", "waktu_absen", "ambil_jatah_makan"]
	)

	attendance_map = {}

	for record in attendance_records:
		karyawan = record.karyawan
		karyawan_doc = frappe.get_doc("Karyawan", karyawan)
		nama_lengkap = karyawan_doc.nama_lengkap
		ambil_jatah_makan = record.ambil_jatah_makan
		site = record.lokasi_absen
		tipe = record.tipe
		hari_absen = record.waktu_absen.day

		# Jika hari_absen belum ada di attendance_map, tambahkan
		if hari_absen not in attendance_map:
			attendance_map[hari_absen] = {}

		# Jika site belum ada di hari_absen, tambahkan
		if site not in attendance_map[hari_absen]:
			attendance_map[hari_absen][site] = {}

		# Jika karyawan belum ada di site, tambahkan
		if karyawan not in attendance_map[hari_absen][site]:
			attendance_map[hari_absen][site][karyawan] = {
				"nama_karyawan": nama_lengkap,
				"data_absen": []
			}

		# Tambahkan data absen ke dalam 'data_absen' list
		attendance_map[hari_absen][site][karyawan]["data_absen"].append({
			"tipe": tipe,
			"ambil_jatah_makan": ambil_jatah_makan
		})
 
	return attendance_map

@frappe.whitelist()
def get_attendance_years() -> str:
	"""Returns all the years for which attendance records exist"""
	Attendance = frappe.qb.DocType("Absensi")
	year_list = (
		frappe.qb.from_(Attendance).select(Extract("year", Attendance.waktu_absen).as_("year")).distinct()
	).run(as_dict=True)

	if year_list:
		year_list.sort(key=lambda d: d.year, reverse=True)
	else:
		year_list = [frappe._dict({"year": getdate().year})]

	return "\n".join(cstr(entry.year) for entry in year_list)

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
		days.append({"label": label, "fieldtype": "Data", "fieldname": day})

	return days

def get_total_days_in_month(filters: Filters) -> int:
	return monthrange(cint(filters.year), cint(filters.month))[1]


def get_data(filters) -> list[list]:
    total_days = get_total_days_in_month(filters)
    data_map = {}

    # Misalkan attendance_map adalah hasil dari get_attendance_map(filters)
    attendance_map = get_attendance_map(filters)

    # Iterasi melalui semua hari dalam attendance_map
    for day, site_data in attendance_map.items():
        # Iterasi melalui semua site dalam hari tersebut
        for site, karyawan_data in site_data.items():
            # Iterasi melalui semua karyawan di site tersebut
            for karyawan, attendance in karyawan_data.items():
                nama_lengkap_karyawan = attendance["nama_karyawan"]
                
                # Jika karyawan belum ada di data_map, inisialisasi row baru
                if karyawan not in data_map:
                    # Inisialisasi row dengan NRP, nama karyawan, dan site
                    row = [karyawan, nama_lengkap_karyawan] + [" "] * total_days
                    data_map[karyawan] = row
                else:
                    row = data_map[karyawan]

                # Untuk hari ke-X, tambahkan status kehadiran jika ada
                if day <= total_days:
                    absensi_harian = attendance.get("data_absen", [])
                    hadir = False
                    for absensi in absensi_harian:
                        if absensi["tipe"] == "In" or absensi["tipe"] == "Out":
                            row[2 + day] = '<p style="color: green;">'+site+'</p>';  # Indeks 2 karena data setelah NRP dan nama
                            hadir = True
                            break
                        elif absensi["tipe"] == "Izin":
                            row[2 + day] = '<p style="color: red;">'+site+'</p>';
                            hadir = True
                            break
                    if not hadir:
                        row[2 + day] = " "

    # Convert the data_map values to a list for final output
    return list(data_map.values())



def get_chart_data(attendance_map: dict, filters: Filters) -> dict:
    days = get_columns_for_days(filters)  # Mendapatkan kolom hari dalam bentuk list
    labels = []
    izin = []
    hadir = []
    ambil_jatah_makan = []

    # Iterasi melalui semua hari yang ada
    for day in days:
        date = day['label'].split(' ')[0]  # Mengambil tanggal
        labels.append(date)
        total_hadir_on_day = total_izin_on_day = total_ambil_jatah_makan = 0
        day_index = cint(day["fieldname"])  # Konversi hari ke integer

        # Iterasi melalui hari dalam attendance_map
        for hari_absen, site_data in attendance_map.items():
            if int(hari_absen) == day_index:  # Cocokkan hari absensi dengan hari yang sedang diolah
                # Iterasi melalui site dalam hari tersebut
                for site, karyawan_data in site_data.items():
                    # Iterasi melalui karyawan di setiap site
                    for karyawan, attendance in karyawan_data.items():
                        # Ambil data absensi harian dari karyawan
                        attendance_on_day = attendance.get("data_absen", [])

                        # Variabel untuk melacak apakah karyawan sudah dihitung
                        sudah_hadir = False
                        sudah_ambil_jatah_makan = False

                        # Iterasi melalui setiap entri absensi karyawan
                        for absensi in attendance_on_day:
                            if absensi["tipe"] == "Izin":
                                total_izin_on_day += 1
                            elif absensi["tipe"] in ["In", "Out", "Work From Home"]:
                                if not sudah_hadir:  # Hanya hitung sekali per karyawan per hari
                                    total_hadir_on_day += 1
                                    sudah_hadir = True  # Menandai karyawan sudah dihitung

                                # Jika ada jatah makan diambil, tambahkan ke total
                                if absensi["ambil_jatah_makan"] and not sudah_ambil_jatah_makan:
                                    total_ambil_jatah_makan += 1
                                    sudah_ambil_jatah_makan = True  # Menandai jatah makan sudah dihitung

        # Tambahkan hasil perhitungan untuk hari ini ke dalam list
        izin.append(total_izin_on_day)
        hadir.append(total_hadir_on_day)
        ambil_jatah_makan.append(total_ambil_jatah_makan)

    # Return data dalam format yang diminta (untuk chart)
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

