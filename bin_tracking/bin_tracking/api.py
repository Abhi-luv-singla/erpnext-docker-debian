"""
Bin Tracking API Module
Canonical, whitelisted API surface for barcode scanning, item/bin lookup,
and bin-to-bin stock transfer operations.

This module consolidates what used to be three overlapping implementations
(this file, bin_transfer_api.py, and pages/bin_transfer/bin_transfer.py) into
a single best-of-breed implementation. The frontend must call methods on
this module only.
"""
import frappe
from frappe import _
from frappe.utils import now
from bin_tracking.bin_tracking.doctype.bin_stock.bin_stock import get_bin_stock
from bin_tracking.utils import check_bin_exists


# ============================================================================
# BARCODE SCANNING METHODS
# ============================================================================

@frappe.whitelist()
def scan_item_barcode(barcode):
	"""
	Scan and process item barcode

	Args:
		barcode (str): Item barcode to scan

	Returns:
		dict: Item details or error message
	"""
	try:
		if not barcode or not barcode.strip():
			return {
				"success": False,
				"error": _("Barcode cannot be empty")
			}

		barcode = barcode.strip()

		# Look up item by barcode
		item_barcode = frappe.db.get_value(
			"Item Barcode",
			{"barcode": barcode},
			["parent", "barcode"],
			as_dict=True
		)

		if not item_barcode:
			return {
				"success": False,
				"error": _("Barcode '{0}' not found in system").format(barcode),
				"barcode": barcode
			}

		# Get item details
		item_doc = frappe.get_doc("Item", item_barcode.get("parent"))

		return {
			"success": True,
			"item_code": item_doc.item_code,
			"item_name": item_doc.item_name,
			"description": item_doc.description or "",
			"stock_uom": item_doc.stock_uom,
			"barcode": barcode,
			"item_group": item_doc.item_group,
			"brand": item_doc.brand or "",
			"disabled": item_doc.disabled
		}

	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied. You don't have access to scan items")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Barcode Scan Error")
		return {
			"success": False,
			"error": _("Error scanning barcode: {0}").format(str(e))
		}


@frappe.whitelist()
def scan_bin_barcode(barcode):
	"""
	Scan and process bin barcode/QR code

	Args:
		barcode (str): Bin barcode or QR code data

	Returns:
		dict: Bin details with contents or error message
	"""
	try:
		if not barcode or not barcode.strip():
			return {
				"success": False,
				"error": _("Bin barcode cannot be empty")
			}

		barcode = barcode.strip()

		# Get bin details
		bin_doc = frappe.get_doc("Warehouse Bin", barcode)

		# Get bin contents
		contents = frappe.db.get_list(
			"Bin Stock",
			filters={"warehouse_bin": barcode},
			fields=["item_code", "item_name", "quantity", "uom", "name"],
			order_by="item_code asc"
		)

		# Get warehouse hierarchy
		warehouse = None
		warehouse_zone = None

		if bin_doc.warehouse_rack:
			warehouse_zone_doc = frappe.get_value(
				"Warehouse Rack",
				bin_doc.warehouse_rack,
				"warehouse_zone"
			)
			if warehouse_zone_doc:
				warehouse = frappe.get_value(
					"Warehouse Zone",
					warehouse_zone_doc,
					"warehouse"
				)
				warehouse_zone = warehouse_zone_doc

		return {
			"success": True,
			"bin": {
				"name": bin_doc.name,
				"bin_number": bin_doc.bin_number,
				"bin_code": bin_doc.bin_code or "",
				"warehouse_rack": bin_doc.warehouse_rack or "",
				"warehouse_zone": warehouse_zone,
				"warehouse": warehouse,
				"capacity": bin_doc.capacity or 0,
				"is_active": bin_doc.is_active
			},
			"contents": contents,
			"total_items": len(contents),
			"total_quantity": sum(item.get("quantity", 0) for item in contents)
		}

	except frappe.DoesNotExistError:
		return {
			"success": False,
			"error": _("Bin '{0}' not found").format(barcode),
			"barcode": barcode
		}
	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied. You don't have access to view this bin")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Bin Barcode Scan Error")
		return {
			"success": False,
			"error": _("Error scanning bin: {0}").format(str(e))
		}


# ============================================================================
# ITEM LOOKUP METHODS
# ============================================================================

@frappe.whitelist()
def get_item_details(item_code):
	"""
	Get detailed item information

	Args:
		item_code (str): Item code to look up

	Returns:
		dict: Item details or error message
	"""
	try:
		if not item_code or not item_code.strip():
			return {
				"success": False,
				"error": _("Item code cannot be empty")
			}

		item_code = item_code.strip()

		item_doc = frappe.get_doc("Item", item_code)

		# Get all barcodes for this item
		barcodes = frappe.db.get_list(
			"Item Barcode",
			filters={"parent": item_code},
			fields=["barcode", "uom"]
		)

		return {
			"success": True,
			"item_code": item_doc.item_code,
			"item_name": item_doc.item_name,
			"description": item_doc.description or "",
			"item_group": item_doc.item_group,
			"brand": item_doc.brand or "",
			"stock_uom": item_doc.stock_uom,
			"disabled": item_doc.disabled,
			"barcodes": barcodes,
			"weight_per_unit": item_doc.weight_per_unit or 0,
			"weight_uom": item_doc.weight_uom or ""
		}

	except frappe.DoesNotExistError:
		return {
			"success": False,
			"error": _("Item '{0}' not found").format(item_code),
			"item_code": item_code
		}
	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied. You don't have access to view this item")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Item Lookup Error")
		return {
			"success": False,
			"error": _("Error looking up item: {0}").format(str(e))
		}


@frappe.whitelist()
def get_item_stock_locations(item_code):
	"""
	Get all bins where an item is stored

	Args:
		item_code (str): Item code to search

	Returns:
		dict: List of bins with quantities or error message
	"""
	try:
		if not item_code or not item_code.strip():
			return {
				"success": False,
				"error": _("Item code cannot be empty")
			}

		item_code = item_code.strip()

		# Verify item exists
		frappe.get_doc("Item", item_code)

		# Get all locations with this item
		locations = frappe.db.get_list(
			"Bin Stock",
			filters={"item_code": item_code},
			fields=["warehouse_bin", "quantity", "uom", "name"],
			order_by="warehouse_bin asc"
		)

		# Enrich with bin details
		enriched_locations = []
		total_quantity = 0

		for location in locations:
			try:
				bin_doc = frappe.get_doc("Warehouse Bin", location.get("warehouse_bin"))
				total_quantity += location.get("quantity", 0)

				enriched_locations.append({
					"bin_code": bin_doc.name,
					"bin_number": bin_doc.bin_number,
					"warehouse_rack": bin_doc.warehouse_rack or "",
					"quantity": location.get("quantity", 0),
					"uom": location.get("uom", ""),
					"bin_stock_id": location.get("name")
				})
			except Exception:
				# Include location even if bin details fail
				enriched_locations.append({
					"bin_code": location.get("warehouse_bin"),
					"quantity": location.get("quantity", 0),
					"uom": location.get("uom", "")
				})

		return {
			"success": True,
			"item_code": item_code,
			"locations": enriched_locations,
			"total_quantity": total_quantity,
			"location_count": len(enriched_locations)
		}

	except frappe.DoesNotExistError:
		return {
			"success": False,
			"error": _("Item '{0}' not found").format(item_code),
			"item_code": item_code
		}
	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Item Stock Locations Error")
		return {
			"success": False,
			"error": _("Error retrieving stock locations: {0}").format(str(e))
		}


# ============================================================================
# BIN STOCK / AVAILABILITY METHODS
# ============================================================================

@frappe.whitelist()
def get_bin_stock_details(warehouse_bin):
	"""
	Get all item stock contents of a specific bin

	Args:
		warehouse_bin (str): Warehouse Bin code

	Returns:
		dict: List of item stock entries in the bin or error message
	"""
	try:
		if not warehouse_bin or not warehouse_bin.strip():
			return {
				"success": False,
				"error": _("Warehouse bin cannot be empty")
			}

		warehouse_bin = warehouse_bin.strip()

		if not check_bin_exists(warehouse_bin):
			return {
				"success": False,
				"error": _("Bin '{0}' not found").format(warehouse_bin)
			}

		contents = frappe.db.get_list(
			"Bin Stock",
			filters={"warehouse_bin": warehouse_bin},
			fields=["item_code", "item_name", "quantity", "uom", "name"],
			order_by="item_code asc"
		)

		return {
			"success": True,
			"warehouse_bin": warehouse_bin,
			"contents": contents,
			"total_items": len(contents),
			"total_quantity": sum(item.get("quantity", 0) for item in contents)
		}

	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied. You don't have access to view this bin")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Bin Stock Details Error")
		return {
			"success": False,
			"error": _("Error retrieving bin stock details: {0}").format(str(e))
		}


@frappe.whitelist()
def get_available_bins(warehouse_zone):
	"""
	Get all active bins within a warehouse zone (for destination bin picker)

	Args:
		warehouse_zone (str): Warehouse Zone code

	Returns:
		dict: List of active bins in the zone or error message
	"""
	try:
		if not warehouse_zone or not warehouse_zone.strip():
			return {
				"success": False,
				"error": _("Warehouse zone cannot be empty")
			}

		warehouse_zone = warehouse_zone.strip()

		racks = frappe.db.get_list(
			"Warehouse Rack",
			filters={"warehouse_zone": warehouse_zone, "is_active": 1},
			fields=["name"]
		)

		bins = []
		for rack in racks:
			bin_list = frappe.db.get_list(
				"Warehouse Bin",
				filters={"warehouse_rack": rack.name, "is_active": 1},
				fields=["name", "bin_number", "warehouse_rack"]
			)
			bins.extend(bin_list)

		return {
			"success": True,
			"warehouse_zone": warehouse_zone,
			"bins": bins,
			"bin_count": len(bins)
		}

	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Get Available Bins Error")
		return {
			"success": False,
			"error": _("Error retrieving available bins: {0}").format(str(e))
		}


# ============================================================================
# TRANSFER PROCESSING METHODS
# ============================================================================

@frappe.whitelist()
def validate_transfer(item_code, source_bin, destination_bin, quantity):
	"""
	Validate if a transfer operation is possible

	Args:
		item_code (str): Item to transfer
		source_bin (str): Source bin code
		destination_bin (str): Destination bin code
		quantity (float): Quantity to transfer

	Returns:
		dict: Validation result with details
	"""
	try:
		# Validate inputs
		if not all([item_code, source_bin, destination_bin, quantity]):
			return {
				"success": False,
				"error": _("All fields are required"),
				"valid": False
			}

		try:
			quantity = float(quantity)
			if quantity <= 0:
				return {
					"success": False,
					"error": _("Quantity must be greater than 0"),
					"valid": False
				}
		except (ValueError, TypeError):
			return {
				"success": False,
				"error": _("Invalid quantity format"),
				"valid": False
			}

		# Check if source and destination are different
		if source_bin == destination_bin:
			return {
				"success": False,
				"error": _("Source and destination bins cannot be the same"),
				"valid": False
			}

		# Verify source bin exists
		if not check_bin_exists(source_bin):
			return {
				"success": False,
				"error": _("Source bin '{0}' not found").format(source_bin),
				"valid": False
			}

		# Verify destination bin exists and is active
		if not check_bin_exists(destination_bin):
			return {
				"success": False,
				"error": _("Destination bin '{0}' not found").format(destination_bin),
				"valid": False
			}

		dest_bin_doc = frappe.get_doc("Warehouse Bin", destination_bin)
		if not dest_bin_doc.is_active:
			return {
				"success": False,
				"error": _("Destination bin is inactive"),
				"valid": False
			}

		# Verify item exists
		try:
			frappe.get_doc("Item", item_code)
		except frappe.DoesNotExistError:
			return {
				"success": False,
				"error": _("Item '{0}' not found").format(item_code),
				"valid": False
			}

		# Check available quantity in source bin
		available_qty = get_bin_stock(source_bin, item_code)

		if available_qty < quantity:
			return {
				"success": False,
				"error": _("Insufficient quantity in source bin. Available: {0}, Requested: {1}").format(
					available_qty, quantity
				),
				"valid": False,
				"available_quantity": available_qty
			}

		# Check destination bin capacity
		if dest_bin_doc.capacity and dest_bin_doc.capacity > 0:
			dest_contents = frappe.db.get_value(
				"Bin Stock",
				{"warehouse_bin": destination_bin, "item_code": item_code},
				"quantity"
			) or 0
			total_after_transfer = dest_contents + quantity
			if total_after_transfer > dest_bin_doc.capacity:
				return {
					"success": False,
					"error": _("Transfer would exceed destination bin capacity. Max: {0}, Would be: {1}").format(
						dest_bin_doc.capacity, total_after_transfer
					),
					"valid": False,
					"capacity_limit": dest_bin_doc.capacity,
					"would_exceed_by": total_after_transfer - dest_bin_doc.capacity
				}

		return {
			"success": True,
			"valid": True,
			"message": _("Transfer is valid and can proceed"),
			"source_available": available_qty,
			"transfer_quantity": quantity
		}

	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied"),
			"valid": False
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Transfer Validation Error")
		return {
			"success": False,
			"error": _("Error validating transfer: {0}").format(str(e)),
			"valid": False
		}


@frappe.whitelist()
def process_transfer(item_code, source_bin, destination_bin, quantity, remarks=""):
	"""
	Process a bin-to-bin transfer

	Args:
		item_code (str): Item to transfer
		source_bin (str): Source bin code
		destination_bin (str): Destination bin code
		quantity (float): Quantity to transfer
		remarks (str): Optional transfer remarks

	Returns:
		dict: Transfer result with document details
	"""
	try:
		# NOTE: validate_transfer() here is a fast-fail UX check only, so the
		# caller gets an immediate, friendly error message (e.g. insufficient
		# stock, capacity exceeded) without round-tripping through document
		# insert/submit. It reads Bin Stock without any row lock, so under
		# concurrent requests two callers can both pass this check for the
		# same source bin ("time-of-check" race). That is expected and fine:
		# Bin Stock quantity locking (SELECT ... FOR UPDATE) happens in
		# BinTransfer.on_submit (doctype layer, bin_transfer.py) — that is the
		# authoritative guard against oversubscribing a bin. Do not add
		# locking here; it would duplicate/conflict with the doctype-layer
		# fix and this function has no business owning that concern.
		validation = validate_transfer(item_code, source_bin, destination_bin, quantity)
		if not validation.get("valid"):
			return validation

		quantity = float(quantity)

		# Create transfer document
		transfer_doc = frappe.new_doc("Bin Transfer")
		transfer_doc.item_code = item_code
		transfer_doc.source_bin = source_bin
		transfer_doc.destination_bin = destination_bin
		transfer_doc.quantity = quantity
		transfer_doc.transfer_date = now()
		transfer_doc.transferred_by = frappe.session.user

		if remarks and remarks.strip():
			transfer_doc.remarks = remarks.strip()

		# Insert the document
		transfer_doc.insert(ignore_permissions=False)

		# Submit the document. This triggers BinTransfer.on_submit(), which
		# performs the authoritative (locked) read-modify-write of Bin Stock
		# quantities. If two concurrent requests both got past the
		# validate_transfer() fast-fail check above, this is where the
		# doctype-layer lock is expected to serialize them and where the
		# second one should raise (e.g. insufficient stock) instead of
		# silently oversubscribing the source bin.
		transfer_doc.submit()

		return {
			"success": True,
			"message": _("Transfer completed successfully"),
			"transfer_id": transfer_doc.name,
			"item_code": item_code,
			"source_bin": source_bin,
			"destination_bin": destination_bin,
			"quantity": quantity,
			"transfer_date": transfer_doc.transfer_date,
			"transferred_by": transfer_doc.transferred_by,
			"status": transfer_doc.docstatus
		}

	except frappe.DuplicateEntryError:
		return {
			"success": False,
			"error": _("A similar transfer is already in progress")
		}
	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied. You don't have permission to create transfers")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Process Transfer Error")
		return {
			"success": False,
			"error": _("Error processing transfer: {0}").format(str(e))
		}


@frappe.whitelist()
def get_transfer_history(item_code=None, source_bin=None, destination_bin=None, limit=50):
	"""
	Get transfer history with optional filters

	Args:
		item_code (str): Optional filter by item
		source_bin (str): Optional filter by source bin
		destination_bin (str): Optional filter by destination bin
		limit (int): Number of records to return

	Returns:
		dict: List of transfers or error message
	"""
	try:
		filters = {}

		if item_code and item_code.strip():
			filters["item_code"] = item_code.strip()

		if source_bin and source_bin.strip():
			filters["source_bin"] = source_bin.strip()

		if destination_bin and destination_bin.strip():
			filters["destination_bin"] = destination_bin.strip()

		try:
			limit = int(limit)
			if limit <= 0:
				limit = 50
		except (ValueError, TypeError):
			limit = 50

		transfers = frappe.db.get_list(
			"Bin Transfer",
			filters=filters,
			fields=[
				"name",
				"item_code",
				"item_name",
				"source_bin",
				"destination_bin",
				"quantity",
				"uom",
				"transfer_date",
				"transferred_by",
				"docstatus",
				"remarks"
			],
			order_by="transfer_date desc",
			limit_page_length=limit
		)

		return {
			"success": True,
			"transfers": transfers,
			"total_count": len(transfers),
			"filters": filters
		}

	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Transfer History Error")
		return {
			"success": False,
			"error": _("Error retrieving transfer history: {0}").format(str(e))
		}


@frappe.whitelist()
def get_transfer_details(transfer_id):
	"""
	Get detailed information about a specific transfer

	Args:
		transfer_id (str): Transfer document ID

	Returns:
		dict: Transfer details or error message
	"""
	try:
		if not transfer_id or not transfer_id.strip():
			return {
				"success": False,
				"error": _("Transfer ID cannot be empty")
			}

		transfer_doc = frappe.get_doc("Bin Transfer", transfer_id.strip())

		return {
			"success": True,
			"transfer": {
				"id": transfer_doc.name,
				"item_code": transfer_doc.item_code,
				"item_name": transfer_doc.item_name,
				"source_bin": transfer_doc.source_bin,
				"destination_bin": transfer_doc.destination_bin,
				"quantity": transfer_doc.quantity,
				"uom": transfer_doc.uom,
				"transfer_date": transfer_doc.transfer_date,
				"transferred_by": transfer_doc.transferred_by,
				"remarks": transfer_doc.remarks or "",
				"status": "Submitted" if transfer_doc.docstatus == 1 else "Draft",
				"docstatus": transfer_doc.docstatus,
				"creation": transfer_doc.creation,
				"modified": transfer_doc.modified
			}
		}

	except frappe.DoesNotExistError:
		return {
			"success": False,
			"error": _("Transfer '{0}' not found").format(transfer_id)
		}
	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Transfer Details Error")
		return {
			"success": False,
			"error": _("Error retrieving transfer details: {0}").format(str(e))
		}


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@frappe.whitelist()
def batch_transfer(transfers_data):
	"""
	Process multiple transfers in batch

	Args:
		transfers_data (str or list): JSON array of transfer objects
			Each object should have: item_code, source_bin, destination_bin, quantity, remarks

	Returns:
		dict: Batch results with successes and failures
	"""
	try:
		import json

		# Parse input if string
		if isinstance(transfers_data, str):
			transfers_data = json.loads(transfers_data)

		if not isinstance(transfers_data, list):
			return {
				"success": False,
				"error": _("transfers_data must be a list")
			}

		if not transfers_data:
			return {
				"success": False,
				"error": _("transfers_data cannot be empty")
			}

		results = {
			"success": True,
			"successful": [],
			"failed": [],
			"total": len(transfers_data)
		}

		for idx, transfer_data in enumerate(transfers_data):
			try:
				result = process_transfer(
					item_code=transfer_data.get("item_code"),
					source_bin=transfer_data.get("source_bin"),
					destination_bin=transfer_data.get("destination_bin"),
					quantity=transfer_data.get("quantity"),
					remarks=transfer_data.get("remarks", "")
				)

				if result.get("success"):
					results["successful"].append({
						"index": idx,
						"transfer_id": result.get("transfer_id"),
						"item_code": transfer_data.get("item_code")
					})
				else:
					results["failed"].append({
						"index": idx,
						"item_code": transfer_data.get("item_code"),
						"error": result.get("error")
					})

			except Exception as e:
				results["failed"].append({
					"index": idx,
					"item_code": transfer_data.get("item_code"),
					"error": str(e)
				})

		results["successful_count"] = len(results["successful"])
		results["failed_count"] = len(results["failed"])

		return results

	except json.JSONDecodeError:
		return {
			"success": False,
			"error": _("Invalid JSON format in transfers_data")
		}
	except frappe.PermissionError:
		return {
			"success": False,
			"error": _("Permission denied")
		}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Batch Transfer Error")
		return {
			"success": False,
			"error": _("Error processing batch transfer: {0}").format(str(e))
		}
