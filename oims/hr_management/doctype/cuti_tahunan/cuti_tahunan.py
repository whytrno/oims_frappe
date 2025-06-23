import frappe
from frappe.model.document import Document

class CutiTahunan(Document):
    def after_insert(self):
        try:
            # Ambil Jabatan HR
            jabatan_hr = frappe.get_value(
                "Jabatan",
                filters={"name": "HR"},
                fieldname="name"
            )

            if not jabatan_hr:
                frappe.log_error("Tidak ditemukan Jabatan 'HR'")
                return

            # Ambil nama lengkap karyawan pemohon
            nama_karyawan = frappe.get_value(
                "Karyawan",
                filters={"name": self.karyawan_pemohon},
                fieldname="nama_lengkap"
            )

            # Ambil nama + user_id penerima job pending
            nama_penerima, user_penerima = None, None
            penerima_data = frappe.get_value(
                "Karyawan",
                filters={"name": self.karyawan_penerima_job_pending},
                fieldname=["nama_lengkap", "user_id"],
                as_dict=True
            )
            nama_penerima = penerima_data.nama_lengkap
            user_penerima = penerima_data.user_id

            # Deskripsi untuk HR
            description_hr = f"""
{nama_karyawan} mengajukan cuti tahunan:

🗓️ Tanggal Cuti: {self.tanggal_mulai_cuti} s.d. {self.tanggal_selesai_cuti}
📅 Selama: {self.selama_hari} hari
🎯 Keperluan: {self.keperluan}
🔁 Penerima tugas selama cuti: {nama_penerima or '-'}
"""

            # Notifikasi ke HR
            frappe.get_doc({
                "doctype": "OIMS Notification",
                "title": "Pengajuan Cuti Tahunan Baru",
                "description": description_hr.strip(),
                "jabatan": jabatan_hr,
                "type": "Cuti",
                "link_to": f"{frappe.get_hooks('website_url')[0]}/form-cuti-tahunan/{self.name}",
                "link_to_label": "Lihat Pengajuan Cuti"
            }).insert(ignore_permissions=True)

            # Notifikasi ke penerima tugas (user langsung)
            if user_penerima:
                description_penerima = f"""
Anda ditunjuk oleh {nama_karyawan} untuk menerima tugas selama masa cuti:

🗓️ {self.tanggal_mulai_cuti} s.d. {self.tanggal_selesai_cuti}
📅 Total: {self.selama_hari} hari
📄 Harap tandatangani formulir cuti tahunan secepatnya.
"""

                frappe.get_doc({
                    "doctype": "OIMS Notification",
                    "title": "Tanda Tangan Pengalihan Tugas Cuti",
                    "description": description_penerima.strip(),
                    "user": user_penerima,
                    "type": "Cuti",
                    "link_to": f"{frappe.get_hooks('website_url')[0]}/form-cuti-tahunan/{self.name}/edit",
                    "link_to_label": "Tandatangani Formulir"
                }).insert(ignore_permissions=True)

        except Exception as e:
            frappe.log_error(f"Failed to create OIMS Notification for CutiTahunan: {str(e)}")
