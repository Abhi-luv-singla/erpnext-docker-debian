from frappe.model.document import Document
import frappe


class BinStock(Document):
	def validate(self):
		if self.quantity < 0:
			frappe.throw("Quantity cannot be negative")

		existing = frappe.db.get_value(
			"Bin Stock",
			{"warehouse_bin": self.warehouse_bin, "item_code": self.item_code, "name": ["!=", self.name]},
			"name",
		)
		if existing:
			frappe.throw(f"Bin Stock record already exists for this item in this bin: {existing}")


def get_bin_stock(warehouse_bin, item_code):
	try:
		return frappe.get_value("Bin Stock", {"warehouse_bin": warehouse_bin, "item_code": item_code}, "quantity") or 0
	except:
		return 0


def update_bin_stock(warehouse_bin, item_code, quantity, remarks=""):
	stock = frappe.get_value("Bin Stock", {"warehouse_bin": warehouse_bin, "item_code": item_code}, "name")

	if stock:
		bin_stock_doc = frappe.get_doc("Bin Stock", stock)
		bin_stock_doc.quantity = quantity
		if remarks:
			bin_stock_doc.remarks = remarks
		bin_stock_doc.save()
	else:
		bin_stock_doc = frappe.new_doc("Bin Stock")
		bin_stock_doc.warehouse_bin = warehouse_bin
		bin_stock_doc.item_code = item_code
		bin_stock_doc.quantity = quantity
		if remarks:
			bin_stock_doc.remarks = remarks
		bin_stock_doc.insert()

	return bin_stock_doc
