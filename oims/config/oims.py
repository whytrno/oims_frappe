from frappe import _

def get_data():
    return [
        {
            "label": _("Oims"),
            "icon": "octicon octicon-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "Karyawan",
                    "label": _("Karyawan"),
                    "description": _("Manage Books"),
                    "onboard": 1,
                },
            ]
        }
    ]
