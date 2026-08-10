import frappe
import qrcode
import io
import base64
from frappe import _


def generate_qr_code(data):
	"""Generate QR code image from data"""
	try:
		qr = qrcode.QRCode(
			version=1,
			error_correction=qrcode.constants.ERROR_CORRECT_L,
			box_size=10,
			border=4,
		)
		qr.add_data(data)
		qr.make(fit=True)

		img = qr.make_image(fill_color="black", back_color="white")
		buffer = io.BytesIO()
		img.save(buffer, format='PNG')
		buffer.seek(0)

		return f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"
	except Exception as e:
		frappe.log_error(f"Error generating QR code: {str(e)}")
		return None


def get_item_barcode(item_code):
	"""Get barcode for item"""
	try:
		barcode = frappe.db.get_value("Item Barcode", {"parent": item_code}, "barcode")
		return barcode
	except:
		return None


def get_warehouse_hierarchy(warehouse_name):
	"""Get all zones, racks, and bins for a warehouse"""
	try:
		zones = frappe.db.get_list(
			"Warehouse Zone",
			filters={"warehouse": warehouse_name, "is_active": 1},
			fields=["name", "zone_name", "zone_type"]
		)

		result = {"warehouse": warehouse_name, "zones": []}

		for zone in zones:
			racks = frappe.db.get_list(
				"Warehouse Rack",
				filters={"warehouse_zone": zone["name"], "is_active": 1},
				fields=["name", "rack_code", "rack_name"]
			)

			zone_data = {
				"zone_name": zone["name"],
				"zone_type": zone["zone_type"],
				"racks": []
			}

			for rack in racks:
				bins = frappe.db.get_list(
					"Warehouse Bin",
					filters={"warehouse_rack": rack["name"], "is_active": 1},
					fields=["name", "bin_number", "bin_code", "capacity"]
				)

				rack_data = {
					"rack_name": rack["name"],
					"rack_code": rack["rack_code"],
					"bins": bins
				}
				zone_data["racks"].append(rack_data)

			result["zones"].append(zone_data)

		return result
	except Exception as e:
		frappe.log_error(f"Error getting warehouse hierarchy: {str(e)}")
		return None


def check_bin_exists(bin_code):
	"""Check if bin exists. Used by api.py's validate_transfer/get_bin_stock_details
	as the single canonical bin-existence check (avoids fetching a full doc just
	to test presence)."""
	try:
		return frappe.db.exists("Warehouse Bin", bin_code)
	except Exception:
		return False
