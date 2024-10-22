# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

from calendar import monthrange
from itertools import groupby

import frappe
from frappe import _
from frappe.query_builder.functions import Count, Extract, Sum
from frappe.utils import cint, cstr, getdate, add_days, date_diff
from frappe.utils.nestedset import get_descendants_of

Filters = frappe._dict

status_map = {
	"Hadir": "H",
	"Telat": "T",
	"Izin": "I",
	"Work From Home": "WFH",
}

day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def execute(filters: Filters | None = None):
    if not (filters.month and filters.year):
        filters.month, filters.year, filters.minggu_ke = getdate().month, getdate().year

    # Jika filter perbulan tidak dipilih, cek minggu ke berapa
    if filters.minggu_ke and cint(filters.minggu_ke) > 1:
        start_date, _, end_date, _ = get_week_date_range(filters)
        filters.start_date = start_date
        filters.end_date = end_date
    else:
        filters.start_date = f"{filters.year}-{filters.month}-01"
        filters.end_date = f"{filters.year}-{filters.month}-{monthrange(int(filters.year), int(filters.month))[1]}"

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
    # Cek apakah tanggal start_date dan end_date sudah ada di filter
    if filters.start_date and filters.end_date:
        date_range = (filters.start_date, filters.end_date)
    else:
        date_range = (f"{filters.year}-{filters.month}-01", f"{filters.year}-{filters.month}-{monthrange(int(filters.year), int(filters.month))[1]}")

    attendance_records = frappe.get_all(
        "Absensi",
        filters={
            "waktu_absen": ["between", date_range],
        },
        fields=["lokasi_absen", "karyawan", "tipe", "waktu_absen", "ambil_jatah_makan", "telat"]
    )

    if filters.site:
        attendance_records = [record for record in attendance_records if record.lokasi_absen == filters.site]

    attendance_map = {}

    for record in attendance_records:
        karyawan = record.karyawan
        karyawan_doc = frappe.get_doc("Karyawan", karyawan)
        nama_lengkap = karyawan_doc.nama_lengkap
        ambil_jatah_makan = record.ambil_jatah_makan
        site = record.lokasi_absen
        tipe = record.tipe
        telat = record.telat
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
            "ambil_jatah_makan": ambil_jatah_makan,
            "telat": telat
        })

    return attendance_map

def get_week_date_range(filters):
    """Mengembalikan rentang tanggal untuk minggu ke berapa yang dipilih"""
    minggu_ke = cint(filters.minggu_ke)
    year = cint(filters.year)
    month = cint(filters.month)

    first_day_of_month = getdate(f"{year}-{month}-01")
    first_weekday = first_day_of_month.weekday()  # Dapatkan weekday dari hari pertama bulan ini (0: Senin)

    if minggu_ke == 1:
        # Jika minggu ke-1 dipilih, maka pilih seluruh bulan
        start_date = first_day_of_month
        end_date = getdate(f"{year}-{month}-{monthrange(year, month)[1]}")
        start_day_of_week = first_day_of_month
        end_day_of_week = end_date
    else:
        # Hitung rentang minggu untuk minggu ke-2, ke-3, dst.
        # Karena `minggu_ke = 2` mewakili minggu ke-1, kita perlu menyesuaikan perhitungannya.
        start_day_of_week = (minggu_ke - 2) * 7  # Minggu pertama dimulai dari hari pertama bulan
        end_day_of_week = start_day_of_week + 6
        start_date = add_days(first_day_of_month, start_day_of_week)

        # Akhiri minggu pada akhir pekan atau akhir bulan, mana yang lebih dulu
        end_date = add_days(start_date, 6)
        end_of_month = getdate(f"{year}-{month}-{monthrange(year, month)[1]}")

        if end_date > end_of_month:
            end_date = end_of_month

    return start_date, start_day_of_week, end_date, end_day_of_week

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
    # Menghitung total hari berdasarkan filter start_date dan end_date
    start_date = getdate(filters.start_date)
    end_date = getdate(filters.end_date)
    days = []
    current_date = start_date

    while current_date <= end_date:
        day = cstr(current_date.day)
        weekday = day_abbr[current_date.weekday()]
        label = f"{day} {weekday}"
        days.append({"label": label, "fieldtype": "Data", "fieldname": day})
        current_date = add_days(current_date, 1)

    return days

def get_total_days_in_month(filters: Filters) -> int:
    return monthrange(cint(filters.year), cint(filters.month))[1]

def get_data(filters) -> list[list]:
    total_days = get_total_days_in_month(filters)
    data_map = {}
    
    # Untuk hari ke-X, tambahkan status kehadiran jika ada
    minggu_ke = cint(filters.minggu_ke)
    _, start_date_day, _, end_date_day = get_week_date_range(filters)

    if minggu_ke > 1:
        total_days = 7

    # Misalkan attendance_map adalah hasil dari get_attendance_map(filters)
    attendance_map = get_attendance_map(filters)

    # Iterasi melalui semua hari dalam attendance_map
    for day, site_data in attendance_map.items():
        if minggu_ke > 1:
            day = day - ((minggu_ke - 2) * 7)
            
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
                
                if day <= total_days:
                    absensi_harian = attendance.get("data_absen", [])
                    hadir = False
                    for absensi in absensi_harian:
                        if absensi["tipe"] == "In" or absensi["tipe"] == "Out":
                            if absensi["tipe"] == "In" and absensi["telat"]:
                                row[1 + day] = '<p style="color: red;">'+site+'</p>';
                                hadir = True
                                break
                            else:
                                row[1 + day] = '<p style="color: green;">'+site+'</p>';
                                hadir = True
                                break
                        elif absensi["tipe"] == "Izin":
                            row[1 + day] = '<p style="color: blue;">'+site+'</p>';
                            hadir = True
                            break
                    if not hadir:
                        row[1 + day] = " "
                        
    # data2 = 
    # Convert the data_map values to a list for final output
    return list(data_map.values())

def get_chart_data(attendance_map: dict, filters: Filters) -> dict:
    # Menyesuaikan chart untuk data harian sesuai rentang tanggal di filter
    start_date = getdate(filters.start_date)
    end_date = getdate(filters.end_date)
    
    labels = []
    izin = []
    hadir = []
    telat = []
    ambil_jatah_makan = []

    # Iterasi melalui rentang tanggal berdasarkan filter
    current_date = start_date
    while current_date <= end_date:
        day = current_date.day
        labels.append(day)
        total_hadir_on_day = total_izin_on_day = total_ambil_jatah_makan = total_telat = 0

        # Iterasi melalui attendance_map untuk menghitung statistik per hari
        if day in attendance_map:
            for site, karyawan_data in attendance_map[day].items():
                for karyawan, attendance in karyawan_data.items():
                    absensi_harian = attendance.get("data_absen", [])
                    for absensi in absensi_harian:
                        if absensi["tipe"] == "In" or absensi["tipe"] == "Out":
                            total_hadir_on_day += 1
                            if absensi["telat"]:
                                total_telat += 1
                        elif absensi["tipe"] == "Izin":
                            total_izin_on_day += 1
                        if absensi["ambil_jatah_makan"]:
                            total_ambil_jatah_makan += 1

        hadir.append(total_hadir_on_day)
        izin.append(total_izin_on_day)
        telat.append(total_telat)
        ambil_jatah_makan.append(total_ambil_jatah_makan)

        # Pindah ke hari berikutnya
        current_date = add_days(current_date, 1)

    chart_data = {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": _("Hadir"), "values": hadir},
                {"name": _("Izin"), "values": izin},
                {"name": _("Telat"), "values": telat},
                {"name": _("Ambil Jatah Makan"), "values": ambil_jatah_makan},
            ],
        },
        "type": "line",  # Bisa juga menggunakan "bar" jika lebih sesuai
    }

    return chart_data



