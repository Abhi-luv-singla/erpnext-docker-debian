from frappe.model.document import Document
import frappe


class WarehouseBin(Document):
	def before_insert(self):
		if not self.qr_code:
			self.generate_qr_code()

	def generate_qr_code(self):
		import qrcode
		import io
		from PIL import Image

		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(self.name)
		qr.make(fit=True)

		img = qr.make_image(fill_color="black", back_color="white")
		buffer = io.BytesIO()
		img.save(buffer, format='PNG')

		import base64
		self.qr_code = self.name
		self.qr_code_image = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
