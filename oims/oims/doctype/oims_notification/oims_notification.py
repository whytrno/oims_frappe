# Copyright (c) 2025, Wahyu Triono and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from pywebpush import webpush, WebPushException

class OIMSNotification(Document):
    def after_insert(self):
        subscribers = frappe.get_all(
            "Push Notification Subscriber",
            filters={"is_subscribed": 1},
            fields=["endpoint", "p256dh", "auth", "user"]
        )

        vapid_private_key = frappe.get_hooks("vapid_private_key")[0]
        vapid_email = frappe.get_hooks("vapid_email")[0]

        payload = {
            "title": self.title,
            "body": self.description or "",
            "url": self.link_to or "",  # Use for redirection
            "tag": self.name  # Unique tag to avoid duplication on client
        }

        for sub in subscribers:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh,
                    "auth": sub.auth
                }
            }

            try:
                webpush(
                    subscription_info=subscription_info,
                    data=frappe.as_json(payload),
                    vapid_private_key=vapid_private_key,
                    vapid_claims={"sub": vapid_email}
                )
            except WebPushException as ex:
                frappe.log_error(f"Web push failed for {sub.user}: {str(ex)}")
                # Optional: mark as unsubscribed if endpoint is invalid
                if "410" in str(ex) or "404" in str(ex):
                    frappe.db.set_value("Push Notification Subscriber", sub.name, "is_subscribed", 0)
