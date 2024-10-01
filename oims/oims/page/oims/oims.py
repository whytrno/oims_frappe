# your_custom_app_name/pages/custom_page.py
import frappe
from frappe import _

def get_context(context):
    context.title = _("Oims Home Page")
