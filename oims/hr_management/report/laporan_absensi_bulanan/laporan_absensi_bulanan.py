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
    "Izin": "I",
    "Telat": "T",
    "Ambil Jatah Makan": "AJM",
}

day_abbr = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def execute(filters: Filters | None = None):
    if not filters:
        filters = Filters()

    if not (filters.month and filters.year):
        today = getdate()
        filters.month, filters.year = today.month, today.year

    # Menentukan rentang tanggal berdasarkan rentang_tanggal
    filters.start_date, filters.end_date = get_date_range(filters)

    # Ambil data absensi
    attendance_map = get_attendance_map(filters)
    if not attendance_map:
        frappe.msgprint(_("No attendance records found."), alert=True, indicator="orange")
        return [], [], None, None

    columns = get_columns(filters)
    data = get_data(attendance_map, filters)

    if not data:
        frappe.msgprint(_("No attendance records found for this criteria."), alert=True, indicator="orange")
        return columns, [], None, None

    message = get_message()
    chart = get_chart_data(attendance_map, filters)

    return columns, data, message, chart

def get_date_range(filters):
    """Mengembalikan rentang tanggal berdasarkan rentang_tanggal filter"""
    today = getdate()
    year, month = cint(filters.year), cint(filters.month)

    if filters.rentang_tanggal == "bulan":
        # Rentang dari awal bulan hingga akhir bulan
        start_date = getdate(f"{year}-{month}-01")
        end_date = getdate(f"{year}-{month}-{monthrange(year, month)[1]}")
    elif filters.rentang_tanggal == "gaji":
        # Rentang dari tanggal 25 bulan sebelumnya hingga tanggal 25 bulan ini
        if month == 1:  # Jika bulan Januari, bulan sebelumnya adalah Desember tahun sebelumnya
            prev_month = 12
            prev_year = year - 1
        else:
            prev_month = month - 1
            prev_year = year

        start_date = getdate(f"{prev_year}-{prev_month}-25")
        end_date = getdate(f"{year}-{month}-25")
    else:
        # Default: jika tidak ada filter rentang_tanggal
        start_date = getdate(f"{year}-{month}-01")
        end_date = getdate(f"{year}-{month}-{monthrange(year, month)[1]}")

    return start_date, end_date

def get_attendance_map(filters):
    from calendar import monthrange

    # Menentukan rentang tanggal
    if filters.start_date and filters.end_date:
        date_range = (filters.start_date, filters.end_date)
    else:
        start_date, end_date = get_week_date_range(filters)
        date_range = (start_date, end_date)

    attendance_records = []

    if filters.perusahaan:
        attendance_records = frappe.get_all(
            "Absensi",
            filters={
                "waktu_absen": ["between", date_range],
                "tipe": "In",
                "karyawan": ["in", frappe.get_all(
                    "Karyawan",
                    filters={
                        "perusahaan": [
                            "in", [filters.perusahaan]
                        ],
                    },
                    pluck="name"
                )]
            },
            fields=["lokasi_absen", "karyawan", "tipe", "waktu_absen", "ambil_jatah_makan", "telat", "izin"],
        )
    else:
        attendance_records = frappe.get_all(
            "Absensi",
            filters={
                "waktu_absen": ["between", date_range],
                "tipe": "In"
            },
            fields=["lokasi_absen", "karyawan", "tipe", "waktu_absen", "ambil_jatah_makan", "telat", "izin"],
        )

    if filters.site:
        attendance_records = [record for record in attendance_records if record.lokasi_absen == filters.site]

    attendance_map = {}

    for record in attendance_records:
        karyawan = record.karyawan
        karyawan_doc = frappe.get_doc("Karyawan", karyawan)
        nama_lengkap = karyawan_doc.nama_lengkap
        karyawan_id = karyawan_doc.name
        nrp = karyawan_doc.nrp
        ambil_jatah_makan = record.ambil_jatah_makan
        jam_absen = record.waktu_absen.strftime("%H:%M")
        site = record.lokasi_absen
        tipe = record.tipe
        telat = record.telat
        izin = record.izin
        waktu_absen = record.waktu_absen
        hari_absen = waktu_absen.day

        # Logika prefiks hari_absen
        if filters.rentang_tanggal == "gaji":
            # Gaji: a untuk bulan awal, b untuk bulan akhir
            if waktu_absen.month == filters.start_date.month:
                prefiks = "a"
            elif waktu_absen.month == filters.end_date.month:
                prefiks = "b"
            else:
                raise ValueError("Tanggal tidak valid dalam rentang gaji.")
            hari_absen = f"{prefiks}{hari_absen}"
        else:
            # Selain gaji: semua prefiks 'a'
            hari_absen = f"a{hari_absen}"

        # Jika hari_absen belum ada di attendance_map, tambahkan
        if hari_absen not in attendance_map:
            attendance_map[hari_absen] = {}

        # Jika site belum ada di hari_absen, tambahkan
        if site not in attendance_map[hari_absen]:
            attendance_map[hari_absen][site] = {}

        # Jika karyawan belum ada di site, tambahkan
        if karyawan_id not in attendance_map[hari_absen][site]:
            attendance_map[hari_absen][site][karyawan_id] = {
                "nama_karyawan": nama_lengkap,
                "data_absen": []
            }

        # Tambahkan data absen ke dalam 'data_absen' list
        attendance_map[hari_absen][site][karyawan_id]["data_absen"].append({
            "tipe": tipe,
            "izin": izin,
            "ambil_jatah_makan": ambil_jatah_makan,
            "telat": telat,
            "jam_absen": jam_absen
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
    else:
        # Hitung rentang minggu untuk minggu ke-2, ke-3, dst.
        # Karena `minggu_ke = 2` mewakili minggu ke-1, kita perlu menyesuaikan perhitungannya.
        start_day_of_week = (minggu_ke - 2) * 7  # Minggu pertama dimulai dari hari pertama bulan
        start_date = add_days(first_day_of_month, start_day_of_week)

        # Akhiri minggu pada akhir pekan atau akhir bulan, mana yang lebih dulu
        end_date = add_days(start_date, 6)
        end_of_month = getdate(f"{year}-{month}-{monthrange(year, month)[1]}")

        if end_date > end_of_month:
            end_date = end_of_month

    return start_date, end_date

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
    colors = ['green', 'blue', 'red', 'purple']

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
                "label": _("ID Pengguna"),
                "fieldname": "id",
                "fieldtype": "Link",
                "options": "Karyawan",
                "width": 120,
            },
            {
                "label": _("Nama karyawan"),
                "fieldname": "nama_karyawan",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": _("Presentase Kehadiran"),
                "fieldname": "presentase_kehadiran",
                "fieldtype": "Data",
                "width": 150
            },
            {
                "label": _("Total Hari Kerja"),
                "fieldname": "total_hari_kerja",
                "fieldtype": "Data",
                "width": 150
            },
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
    abjad = 'a'
    current_date = start_date
    is1 = False

    while current_date <= end_date:
        day = cstr(current_date.day)

        if filters.rentang_tanggal == "gaji":
            if day == "1":
                is1 = True

            if is1:
                abjad = chr(ord('a') + 1)

        weekday = day_abbr[current_date.weekday()]
        label = f"{abjad}{day} {weekday}"
        days.append({"label": label, "fieldtype": "Data", "fieldname": f'{abjad}{day}', "width": 150})
        current_date = add_days(current_date, 1)

    return days

def get_total_days_in_month(filters: Filters) -> int:
    return monthrange(cint(filters.year), cint(filters.month))[1]

def get_data(attendance_map: dict, filters: Filters) -> list[list]:
    data_map = {}

    columns = get_columns(filters)

    for column in columns[3:]:
        fieldname = column['fieldname']
        value = attendance_map.get(fieldname)
        index_now = columns.index(column)


        if value is not None:
            for site, karyawan_data in value.items():
            # Iterasi melalui semua karyawan di site tersebut
                for karyawan, attendance in karyawan_data.items():
                    nama_lengkap_karyawan = attendance["nama_karyawan"]
                    presentase_kehadiran = 0
                    absensi_harian = attendance.get("data_absen", [])

                    if karyawan not in data_map:
                        row = [karyawan, nama_lengkap_karyawan, presentase_kehadiran, 0] + [" "] * len(columns[3:])
                        data_map[karyawan] = row
                    else:
                        row = data_map[karyawan]

                    for absensi in absensi_harian:
                        total_work = int(row[2]) + 1
                        row[2] = total_work
                        row[3] = total_work
                        if absensi["izin"]:
                            row[index_now] = (
                                f'<p style="color: blue;">{site} <small>({absensi["jam_absen"]})</small></p>'
                            )
                            break
                        elif absensi["tipe"] == "In" and absensi["telat"]:
                            row[index_now] = (
                                f'<p style="color: red;">{site} <small>({absensi["jam_absen"]})</small></p>'
                            )
                            break
                        else:
                            row[index_now] = (
                                f'<p style="color: green;">{site} <small>({absensi["jam_absen"]})</small></p>'
                            )
                            break

    for karyawan, row in data_map.items():
        date_now = getdate()
        working_days = 0
        month = filters.month
        year = filters.year

        start_date = getdate(f"{year}-{month}-01")
        if int(month) == date_now.month and int(year) == date_now.year:
            end_date = date_now
        else:
            end_date = getdate(f"{year}-{month}-{monthrange(int(year), int(month))[1]}")

        current_date = start_date

        if filters.rentang_tanggal == "gaji":
            start_date = getdate(f"{year}-{month}-25")
            end_date = getdate(f"{year}-{month}-{monthrange(int(year), int(month))[1]}")

        while current_date <= end_date:
            # weekday() returns 0-6 (Mon-Sun)
            if current_date.weekday() < 5:  # 0-4 adalah Senin-Jumat
                working_days += 1
            current_date = add_days(current_date, 1)

        # Gunakan working_days sebagai pembagi
        row[2] = f'{round((row[2] / working_days) * 100, 2)}%' if working_days > 0 else '0%'
        data_map[karyawan] = row

    data = list(data_map.values())
    return data


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
    months = []
    labels = []

    while current_date <= end_date:
        month = current_date.month
        abjad = 'a'

        if filters.rentang_tanggal == "gaji":
            if month not in months:
                months.append(month)

            abjad = chr(ord('a') + months.index(month))

        day = f'{abjad}{current_date.day}'
        labels.append(day)

        total_hadir_on_day = total_izin_on_day = total_ambil_jatah_makan = total_telat = 0

        # Iterasi melalui attendance_map untuk menghitung statistik per hari
        if day in attendance_map:
            for site, karyawan_data in attendance_map[day].items():
                for karyawan, attendance in karyawan_data.items():
                    absensi_harian = attendance.get("data_absen", [])
                    for absensi in absensi_harian:
                        if absensi["izin"]:
                            total_izin_on_day += 1
                        elif absensi["tipe"] == "In" or absensi["tipe"] == "Out":
                            total_hadir_on_day += 1
                            if absensi["telat"]:
                                total_telat += 1
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
        "type": "bar",
        "colors": ['green', 'blue', 'red', 'purple']
    }

    return chart_data


