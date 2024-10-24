import math

import frappe
from frappe import _
from frappe.query_builder import Order
from frappe.query_builder.functions import Count
from frappe.utils import pretty_date


def get_context(context):
	context.no_cache = 1
	context.parents = [{"name": _("My Account"), "route": "/"}]
	context.body_class = "jobs-page"
	page_len = 20
	filters, txt, sort, offset = get_filters_txt_sort_offset(page_len)
	context.no_of_pages = get_no_of_pages(filters, txt, page_len)
	context.job_openings = get_job_openings(filters, txt, sort, page_len, offset)
	context.all_filters = get_all_filters(filters)
	context.all_filters['jenis_kontrak'] = ['Intership', 'PKWT', 'Project Base']
	context.sort = sort

def get_job_openings(filters=None, txt=None, sort=None, limit=20, offset=0):
	jo = frappe.qb.DocType("Lowongan Pekerjaan")

	query = (
		frappe.qb.from_(jo)
		.select(
			jo.judul,
			jo.route,
			jo.divisi,
			jo.dibuka_pada,
			jo.ditutup_pada,
			jo.jenis_kontrak,
			jo.lokasi,
			jo.publish_gaji,
			jo.gaji_minimal,
			jo.gaji_maksimal,
			jo.dibayarkan_setiap,
			jo.kabupaten_penempatan
		)
		.where((jo.status == "Dibuka") & (jo.publish))
		.limit(limit)
		.offset(offset)
	)

	for d in filters:
		query = query.where(frappe.qb.Field(d).isin(filters[d]))

	if txt:
		query = query.where((jo.judul.like(f"%{txt}%")))

	query = query.orderby("dibuka_pada", order=Order.asc if sort == "asc" else Order.desc)
	results = query.run(as_dict=True)

	for d in results:
		d.dibuka_pada_formatted = pretty_date(d.dibuka_pada)

	return results

def get_no_of_pages(filters=None, txt=None, page_length=20):
	jo = frappe.qb.DocType("Lowongan Pekerjaan")
	query = (
		frappe.qb.from_(jo)
		.select(
			Count("*").as_("no_of_openings"),
		)
		.where((jo.status == "Dibuka") & (jo.publish))
	)

	for d in filters:
		query = query.where(frappe.qb.Field(d).isin(filters[d]))

	if txt:
		query = query.where((jo.judul.like(f"%{txt}%")))

	result = query.run(as_dict=True)

	return math.ceil(result[0].no_of_openings / page_length)


def get_all_filters(filters=None):
	job_openings = frappe.get_all(
		"Lowongan Pekerjaan",
		filters={"publish": 1, "status": "Dibuka"},
		fields=["divisi", "kabupaten_penempatan"],
	)
    
	all_filters = {}
	for opening in job_openings:
		for key, value in opening.items():
			if key in ["divisi", "kabupaten_penempatan"]:
				if value not in all_filters.get(key, []):
					all_filters.setdefault(key, []).append(value)

	return {key: sorted(value) for key, value in all_filters.items()}


def get_filters_txt_sort_offset(page_len=20):
	args = frappe.request.args.to_dict(flat=False)
	filters = {}
	txt = ""
	sort = None
	offset = 0
	allowed_filters = ["divisi", "kabupaten_penempatan", "jenis_kontrak"]

	for d in args:
		if d in allowed_filters:
			filters[d] = args[d]
		elif d == "query":
			txt = args["query"][0]
		elif d == "sort":
			if args["sort"][0]:
				sort = args["sort"][0]
		elif d == "page":
			offset = (int(args["page"][0]) - 1) * page_len

	return filters, txt, sort, offset
