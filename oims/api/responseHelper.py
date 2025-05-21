import frappe

def response_success(message="", data=None):
    res = {
        "success": True,
        "message": message,
    }
    if data is not None:
        res["data"] = data
    return res

def response_error(message="", data=None, http_status_code=400):
    # Set status code jika perlu
    frappe.response["http_status_code"] = http_status_code
    res = {
        "success": False,
        "message": message,
    }
    if data is not None:
        res["data"] = data
    return res
