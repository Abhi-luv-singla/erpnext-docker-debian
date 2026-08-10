from frappe.model.document import Document
import frappe
from frappe import _


class BinTransfer(Document):
	def validate(self):
		from bin_tracking.bin_tracking.doctype.bin_stock.bin_stock import get_bin_stock

		if self.source_bin == self.destination_bin:
			frappe.throw(_("Source and destination bins cannot be the same"))

		if not self.quantity or self.quantity <= 0:
			frappe.throw(_("Quantity must be greater than 0"))

		destination = frappe.db.get_value(
			"Warehouse Bin", self.destination_bin, ["capacity", "is_active"], as_dict=True
		)

		if destination and not destination.is_active:
			frappe.throw(_("Destination bin {0} is inactive").format(self.destination_bin))

		if destination and destination.capacity:
			dest_qty = get_bin_stock(self.destination_bin, self.item_code)
			if dest_qty + self.quantity > destination.capacity:
				frappe.throw(
					_(
						"Destination bin {0} capacity exceeded. Capacity: {1}, Current stock: {2}, Incoming: {3}"
					).format(self.destination_bin, destination.capacity, dest_qty, self.quantity)
				)

		source_qty = get_bin_stock(self.source_bin, self.item_code)
		if source_qty < self.quantity:
			frappe.throw(
				_("Insufficient quantity in source bin. Available: {0}, Requested: {1}").format(
					source_qty, self.quantity
				)
			)

	def on_submit(self):
		self.process_transfer()

	def process_transfer(self):
		from bin_tracking.bin_tracking.doctype.bin_stock.bin_stock import get_bin_stock, update_bin_stock

		# Lock the source Bin Stock row (if it exists) before reading its quantity.
		# This prevents two concurrent transfers from the same bin+item from both
		# reading the same quantity before either writes, which could otherwise
		# oversubscribe the bin. If no row exists yet, there's nothing to lock;
		# the quantity check below will correctly fail since get_bin_stock()
		# returns 0 for a missing row.
		frappe.db.sql(
			"SELECT quantity FROM `tabBin Stock` WHERE warehouse_bin=%s AND item_code=%s FOR UPDATE",
			(self.source_bin, self.item_code),
		)

		source_qty = get_bin_stock(self.source_bin, self.item_code)

		if source_qty < self.quantity:
			frappe.throw(
				_("Insufficient quantity in source bin. Available: {0}, Requested: {1}").format(
					source_qty, self.quantity
				)
			)

		# Deduct from source bin
		if source_qty - self.quantity == 0:
			frappe.delete_doc("Bin Stock", {"warehouse_bin": self.source_bin, "item_code": self.item_code})
		else:
			update_bin_stock(
				self.source_bin,
				self.item_code,
				source_qty - self.quantity,
				f"Transferred to {self.destination_bin}"
			)

		# Lock the destination Bin Stock row (if it exists) before reading/updating
		# its quantity, for the same reason as above but for concurrent transfers
		# landing on the same destination bin+item.
		frappe.db.sql(
			"SELECT quantity FROM `tabBin Stock` WHERE warehouse_bin=%s AND item_code=%s FOR UPDATE",
			(self.destination_bin, self.item_code),
		)

		# Add to destination bin
		dest_qty = get_bin_stock(self.destination_bin, self.item_code)
		update_bin_stock(
			self.destination_bin,
			self.item_code,
			dest_qty + self.quantity,
			f"Transferred from {self.source_bin}"
		)

		# No Stock Ledger Entry needed: bin-to-bin transfers stay within the same
		# Warehouse, so ERPNext's warehouse-level on-hand quantity is unchanged.
		# Bin Stock tracks WHERE within the warehouse, not the warehouse total.


def get_bin_transfer(item_code, source_bin, destination_bin, quantity):
	"""
	Get or create a bin transfer record
	"""
	transfer = frappe.new_doc("Bin Transfer")
	transfer.item_code = item_code
	transfer.source_bin = source_bin
	transfer.destination_bin = destination_bin
	transfer.quantity = quantity
	return transfer
