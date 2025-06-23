import frappe
from frappe.model.document import Document
from pywebpush import webpush, WebPushException

class OIMSNotification(Document):
    def after_insert(self):
        target_users = set()

        # 1. Jika dikirim ke user spesifik
        if self.user:
            target_users.add(self.user)

        # 2. Jika dikirim ke Jabatan tertentu
        elif self.jabatan:
            karyawans = frappe.get_all(
                "Karyawan",
                filters={"jabatan": self.jabatan},
                fields=["user_id"]
            )
            for k in karyawans:
                if k.user_id:
                    target_users.add(k.user_id)

        # 3. Jika dikirim ke semua pengguna
        elif self.semua_pengguna:
            users = frappe.get_all(
                "User",
                filters={"enabled": 1},
                fields=["name"]
            )
            for user in users:
                target_users.add(user.name)

        if not target_users:
            return  # Tidak ada target user

        # 4. Buat dokumen OIMS Notification User untuk setiap user
        for user_id in target_users:
            frappe.get_doc({
                "doctype": "OIMS Notification User",
                "notification": self.name,
                "user": user_id,
                "is_read": 0
            }).insert(ignore_permissions=True)

        # 5. Ambil subscriber aktif dari user yang ditarget
        subscribers = frappe.get_all(
            "Push Notification Subscriber",
            filters={
                "is_subscribed": 1,
                "user": ["in", list(target_users)]
            },
            fields=["name", "endpoint", "p256dh", "auth", "user"]
        )

        if not subscribers:
            return  # Tidak ada subscriber aktif

        # 6. Kirim push notification
        vapid_private_key = frappe.get_hooks("vapid_private_key")[0]
        vapid_email = frappe.get_hooks("vapid_email")[0]

        payload = {
            "title": self.title,
            "body": self.description or "",
            "url": self.link_to or "",
            "tag": self.name
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
                frappe.log_error(
					title="Web push failed for user lathifahputri@orecon.co.id",
					message=str(ex)
				)

                if "410" in str(ex) or "404" in str(ex):
                    frappe.db.set_value("Push Notification Subscriber", sub.name, "is_subscribed", 0)
