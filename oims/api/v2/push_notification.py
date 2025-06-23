import frappe
from datetime import datetime
from oims.api.responseHelper import response_success, response_error

@frappe.whitelist(methods=["POST"])
def create_push_notification_subscription(endpoint, p256dh, auth, device=None):
    try:
        user = frappe.session.user

        if not endpoint or not p256dh or not auth:
            frappe.throw("Missing subscription data")

        existing = frappe.get_all(
            "Push Notification Subscriber",
            filters={
                "user": user,
                "device": device,
            },
            fields=["name"]
        )

        if existing:
            # Update jika endpoint sudah ada (device sudah subscribe sebelumnya)
            doc = frappe.get_doc("Push Notification Subscriber", existing[0].name)
            doc.user = user  # tetap update user, jika misalnya anonymous di awal
            doc.p256dh = p256dh
            doc.auth = auth
            doc.device = device
            doc.is_subscribed = 1
            doc.subscribe_date = datetime.now()
            doc.save()
        else:
            # Simpan device baru
            doc = frappe.new_doc("Push Notification Subscriber")
            doc.user = user
            doc.endpoint = endpoint
            doc.p256dh = p256dh
            doc.auth = auth
            doc.device = device
            doc.is_subscribed = 1
            doc.subscribe_date = datetime.now()
            doc.insert(ignore_permissions=True)

        return response_success("Subscription created successfully")
    except Exception as e:
        frappe.log_error(f"Error creating subscription: {str(e)}")
        return response_error("Failed to create subscription", http_status_code=500)

@frappe.whitelist()
def count_unread_notifications():
    try:
        user = frappe.session.user

        unread_count = frappe.db.count(
            "OIMS Notification User",
            filters={"user": user, "is_read": 0}
        )

        return response_success("Unread notifications count retrieved successfully", data={"unread_count": unread_count})

    except Exception as e:
        frappe.log_error(f"Error counting unread notifications: {str(e)}")
        return response_error("Failed to count unread notifications", http_status_code=500)

@frappe.whitelist()
def get_user_notifications(is_read_filter: bool | None = None) -> dict:
    try:
        user = frappe.session.user

        filters = {"user": user}
        if is_read_filter is not None:
            filters["is_read"] = int(is_read_filter)

        # Ambil OIMS Notification User, lalu join ke OIMS Notification
        notif_users = frappe.get_all(
            "OIMS Notification User",
            filters=filters,
            fields=["name", "notification", "is_read", "creation"],
            order_by="creation desc",
            limit=9999
        )

        notifications = []
        for n in notif_users:
            notif = frappe.get_doc("OIMS Notification", n.notification)
            notifications.append({
                "notification_user_id": n.name,
                "name": notif.name,
                "title": notif.title,
                "description": notif.description,
                "type": notif.type,
                "link_to": notif.link_to,
                "link_to_label": notif.link_to_label,
                "is_read": n.is_read,
                "creation": n.creation.strftime("%Y-%m-%d %H:%M:%S")
            })

        return response_success("Notifications retrieved successfully", data=notifications)

    except Exception as e:
        frappe.log_error(f"Error retrieving notifications: {str(e)}")
        return response_error("Failed to retrieve notifications", http_status_code=500)


@frappe.whitelist(methods=["POST"])
def mark_notification_as_read(name: str):
    try:
        notification = frappe.get_doc("OIMS Notification User", name)
        notification.is_read = 1
        notification.save(ignore_permissions=True)

        return response_success("Notification marked as read successfully")
    except Exception as e:
        frappe.log_error(f"Error marking notification as read: {str(e)}")
        return response_error("Failed to mark notification as read", http_status_code=500)

@frappe.whitelist()
def get_notification_detail(name: str):
    try:
        notification = frappe.get_doc("OIMS Notification", name)

        notification_data = {
            "name": notification.name,
            "title": notification.title,
            "is_read": notification.is_read,
            "description": notification.description,
            "type": notification.type,
            "link_to": notification.link_to,
            "link_to_label": notification.link_to_label,
            "creation": notification.creation.strftime("%Y-%m-%d %H:%M:%S"),
        }

        return response_success("Notification detail retrieved successfully", data=notification_data)
    except Exception as e:
        frappe.log_error(f"Error retrieving notification detail: {str(e)}")
        return response_error("Failed to retrieve notification detail", http_status_code=500)

__all__ = [
    "create_push_notification_subscription",
    "count_unread_notifications",
    "get_user_notifications",
    "mark_notification_as_read",
    "get_notification_detail",
]
