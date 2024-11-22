# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

from calendar import monthrange
from frappe.utils import cint, getdate, add_days
import frappe


Filters = frappe._dict

def execute(filters=Filters):
    columns = get_columns()

    if filters.minggu_ke and cint(filters.minggu_ke) > 1:
        start_date, end_date = get_week_date_range(filters)
        filters.start_date = start_date
        filters.end_date = end_date
    else:
        filters.start_date = f"{filters.year}-{filters.month}-01"
        filters.end_date = f"{filters.year}-{filters.month}-{monthrange(int(filters.year), int(filters.month))[1]}"

    data = get_data(filters)
    chart_data = get_chart_data(filters, data)
    summary = get_summary(data)

    return columns, data, None, chart_data, summary

def get_summary(data):
    """Menghitung total Forecast, Cost, dan Potential dari data"""
    total_forecast = sum(int(row["total"]) for row in data if row["jenis"] == "Forecast")
    total_cost = sum(int(row["total"]) for row in data if row["jenis"] == "Actual")
    total_potential = sum(int(row["total"]) for row in data if row["jenis"] == "Potential")

    summary = [
        {
            "label": "Total Forecast",
            "value": total_forecast,
			"datatype": "Currency",
			"currency": "IDR",
		},
        {
            "label": "Total Cost",
            "value": total_cost,
			"datatype": "Currency",
			"currency": "IDR",
		},
        {
            "label": "Total Potential",
            "value": total_potential,
			"datatype": "Currency",
			"currency": "IDR",
		},
    ]
    return summary

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

def get_columns():
    columns = [
        {"label": "Tanggal", "fieldname": "tanggal", "fieldtype": "Data", "width": 120},
        {"label": "Projek", "fieldname": "projek", "fieldtype": "Data", "width": 120},
        {"label": "Cost/Revenue", "fieldname": "costrevenue", "fieldtype": "Data", "width": 120},
        {"label": "Jenis", "fieldname": "jenis", "fieldtype": "Data", "width": 120},
        {"label": "Total", "fieldname": "total", "fieldtype": "Currency", "options": "IDR", "width": 200},
    ]
    return columns

def get_data(filters=Filters):
    raw_data = frappe.get_all(
        "Forecast Actual Revenue dan Cost",
        filters={
            "tanggal": ["between", (filters.start_date, filters.end_date)],
            "jenis": filters.jenis if filters.jenis != "semua" else None,
            "costrevenue": filters.costrevenue if filters.costrevenue != "semua" else None,
        },
        fields=["tanggal", "projek", "costrevenue", "jenis", "total"],
    )
    data = []

    for row in raw_data:
        # row['tanggal'] = row['tanggal'].day
        existing_row = next((item for item in data if item["tanggal"] == row["tanggal"] and item["jenis"] == row["jenis"] and item["projek"] == row["projek"] and item["costrevenue"] == row["costrevenue"]), None)
        if existing_row:
            existing_row["total"] = int(existing_row["total"]) + int(row["total"])
        else:
            data.append(row)

    return data

def get_chart_data(filters=Filters, raw_data=[]):
    # Ekstrak hanya bagian hari (tanggal) dari tanggal lengkap untuk chart
    labels_data = sorted(list({row["tanggal"].day for row in raw_data}))  # Unique and sorted days as X-axis labels
    datasets = []

    # Dictionary untuk menyimpan total berdasarkan tanggal (hari saja)
    total_forecast = {day: 0 for day in labels_data}
    total_cost = {day: 0 for day in labels_data}
    total_potential = {day: 0 for day in labels_data}

    # Akumulasi total untuk forecast dan cost berdasarkan tanggal
    for row in raw_data:
        day = row["tanggal"].day  # Hanya bagian tanggal
        if row['jenis'] == 'Forecast':
            total_forecast[day] += int(row["total"])
        elif row['jenis'] == 'Actual':
            total_cost[day] += int(row["total"])
        elif row['jenis'] == 'Potential':
            total_potential[day] += int(row["total"])

    # Menambahkan dataset untuk chart dengan angka mentah (numerik)
    datasets.append({
        "name": "Total Forecast",
        "values": [total_forecast[day] for day in labels_data],
    })
    datasets.append({
        "name": "Total Cost",
        "values": [total_cost[day] for day in labels_data],
    })
    datasets.append({
        "name": "Total Potential",
        "values": [total_potential[day] for day in labels_data],
    })

    # Struktur data chart dengan label hanya berupa tanggal
    chart_data = {
        "data": {
            "labels": labels_data,
            "datasets": datasets,
        },
        "type": "bar",
        "colors": ["blue", "red", "yellow"],
		"fieldtype": "Currency",
		"options": "currency",
		"currency": "IDR"
    }

    return chart_data
