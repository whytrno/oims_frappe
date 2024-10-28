# Copyright (c) 2024, Wahyu Triono and contributors
# For license information, please see license.txt

from calendar import monthrange
from frappe.utils import cint, cstr, getdate, add_days, date_diff
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

	return columns, data, None, chart_data

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
			{
				"label": "Tanggal",
				"fieldname": "tanggal",
				"fieldtype": "data",
				"width": 120,
			},
			{
				"label": "Project",
				"fieldname": "project",
				"fieldtype": "data",
				"width": 120,
			},
			{
				"label": "Menu",
				"fieldname": "menu",
				"fieldtype": "data",
				"width": 120,
			},
			{
				"label": "Tipe",
				"fieldname": "tipe",
				"fieldtype": "data",
				"width": 120,
			},
			{
				"label": "Total",
				"fieldname": "total",
				"fieldtype": "data",
				"width": 200,
			},
		]

    return columns

def get_data(filters=Filters):
    print(f'test filters: {filters}')
    raw_data = frappe.get_all(
        "Actual Forecast Potential Project Financial",
        filters={
            "tanggal": ["between", (filters.start_date, filters.end_date)],
            "tipe": filters.tipe if filters.tipe != "semua" else None,
            "menu": filters.menu if filters.menu != "semua" else None,
        },
        fields=["tanggal", "project", "menu", "tipe", "total"],
    )
    data = []

    for row in raw_data:
        existing_row = next((item for item in data if item["tanggal"] == row["tanggal"] and item["tipe"] == row["tipe"] and item["project"] == row["project"] and item["menu"] == row["menu"]), None)
        if existing_row:
            existing_row["total"] = int(existing_row["total"]) + int(row["total"])
        else:
            data.append(row)

    for row in data:
        row["total"] = f"Rp {int(row['total']):,.0f}".replace(",", ".")

    return data

def get_chart_data(filters=Filters, raw_data = []):
    labels_data = []
    datasets = []

    if filters.tipe == "semua":
        data_total_actual = frappe.get_all(
            "Actual Forecast Potential Project Financial",
            filters={
                "tanggal": ["between", (filters.start_date, filters.end_date)],
				"menu": filters.menu if filters.menu != "semua" else None,
                "tipe": "Actual"
            },
            fields=["total"],
        )

        data_total_forecast = frappe.get_all(
            "Actual Forecast Potential Project Financial",
            filters={
                "tanggal": ["between", (filters.start_date, filters.end_date)],
				"menu": filters.menu if filters.menu != "semua" else None,
                "tipe": "Forecast"
            },
            fields=["total"],
        )
        data_total_potential = frappe.get_all(
            "Actual Forecast Potential Project Financial",
            filters={
                "tanggal": ["between", (filters.start_date, filters.end_date)],
				"menu": filters.menu if filters.menu != "semua" else None,
                "tipe": "Potential"
            },
            fields=["total"],
        )

        total_project_per_actual = {}
        for d in data_total_actual:
            # if d.project in total_per_project:
            #     total_per_project[d.project] += int(d.total)
            # else:
            #     total_per_project[d.project] = int(d.total)
            if d.project in total_project_per_actual:
                total_project_per_actual[d.project] += int(d.total)
            else:
                total_project_per_actual[d.project] = int(d.total)

        datasets.append({
            "name": "Actual",
            "values": [d.total for d in data_total_actual]
        })
        datasets.append({
            "name": "Forecast",
            "values": [d.total for d in data_total_forecast]
        })
        datasets.append({
            "name": "Potential",
            "values": [d.total for d in data_total_potential]
        })
    else:
        data_filtered = frappe.get_all(
            "Actual Forecast Potential Project Financial",
            filters={
                "tanggal": ["between", (filters.start_date, filters.end_date)],
				"menu": filters.menu if filters.menu != "semua" else None,
                "tipe": filters.tipe
            },
            fields=["total", "project"],
        )

        total_per_project = {}
        for d in data_filtered:
            if d.project in total_per_project:
                total_per_project[d.project] += int(d.total)
            else:
                total_per_project[d.project] = int(d.total)

        datasets.append({
            "name": filters.tipe,
            "values": list(total_per_project.values())
        })

    for d in raw_data:
        if d.project not in labels_data:
            labels_data.append(d.project)

    chart_data = {
        "data": {
            "labels": labels_data,
            "datasets": datasets,
        },
        "type": "line",
        "colors": ['green', 'blue', 'red', 'purple']
    }

    return chart_data
