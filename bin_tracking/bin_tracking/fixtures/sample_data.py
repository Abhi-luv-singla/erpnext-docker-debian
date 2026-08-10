import frappe
from frappe import _

from bin_tracking.bin_tracking.doctype.bin_stock.bin_stock import update_bin_stock


def create_sample_warehouse_structure():
	"""Create sample warehouse structure for testing"""

	# ERPNext's Warehouse.autoname() always appends " - {company abbr}" to the
	# name when a company is set, so the actual document name is NOT the raw
	# "Faridabad" string below — it's captured from warehouse.name after
	# insert (or lookup) and used for every subsequent Link reference.
	warehouse_title = "Faridabad"

	existing = frappe.db.get_value("Warehouse", {"warehouse_name": warehouse_title}, "name")
	if existing:
		warehouse_name = existing
	else:
		company = frappe.db.get_single_value('Global Defaults', 'default_company') or frappe.db.get_value("Company", {}, "name")
		if not company:
			frappe.throw(_(
				"No Company found. Complete the ERPNext setup wizard (which creates a Company) before running sample data fixtures."
			))
		warehouse = frappe.new_doc("Warehouse")
		warehouse.warehouse_name = warehouse_title
		warehouse.company = company
		warehouse.insert(ignore_permissions=True)
		warehouse_name = warehouse.name
		frappe.logger().info(f"Created warehouse: {warehouse_name}")

	# Create zones
	zones_data = [
		{"zone_name": "Raw Material", "zone_type": "Raw Material"},
		{"zone_name": "WIP", "zone_type": "Work in Progress"},
		{"zone_name": "Packaging", "zone_type": "Packaging"},
		{"zone_name": "Rejection", "zone_type": "Rejection"},
	]

	zones = {}
	for zone_data in zones_data:
		zone_name = f"FAR-{zone_data['zone_name']}"
		if not frappe.db.exists("Warehouse Zone", zone_name):
			zone = frappe.new_doc("Warehouse Zone")
			zone.zone_name = zone_name
			zone.zone_type = zone_data["zone_type"]
			zone.warehouse = warehouse_name
			zone.is_active = 1
			zone.insert(ignore_permissions=True)
			zones[zone_data["zone_name"]] = zone.name
			frappe.logger().info(f"Created zone: {zone_name}")
		else:
			zones[zone_data["zone_name"]] = zone_name

	# Create racks (A, B, C)
	# NOTE: Warehouse Rack uses a naming_series autoname (e.g. "RACK-00001"),
	# so the document name is never the constructed display label below —
	# existence must be checked by real field values, and the real name (not
	# the label) is what downstream code needs for the warehouse_rack Link.
	racks = {}
	for zone_key, zone_name in zones.items():
		for rack_code in ['A', 'B', 'C']:
			rack_display_name = f"{zone_name}-R{rack_code}"
			existing_rack = frappe.db.get_value(
				"Warehouse Rack", {"warehouse_zone": zone_name, "rack_code": rack_code}, "name"
			)
			if existing_rack:
				racks[rack_display_name] = existing_rack
			else:
				rack = frappe.new_doc("Warehouse Rack")
				rack.warehouse_zone = zone_name
				rack.rack_code = rack_code
				rack.rack_name = rack_display_name
				rack.is_active = 1
				rack.insert(ignore_permissions=True)
				racks[rack_display_name] = rack.name
				frappe.logger().info(f"Created rack: {rack_display_name}")

	# Create bins (1-5 per rack)
	# NOTE: racks.values(), not racks.keys() — see the naming_series note above;
	# the dict keys are just display labels, not valid Warehouse Rack Link
	# values. Warehouse Bin is the same story (naming_series "BIN-00001"), so
	# existence is checked by (warehouse_rack, bin_number), not by bin_code.
	bins = {}
	for rack_name in racks.values():
		for bin_num in range(1, 6):
			bin_code = f"{rack_name}-B{bin_num}"
			existing_bin = frappe.db.get_value(
				"Warehouse Bin", {"warehouse_rack": rack_name, "bin_number": f"B{bin_num}"}, "name"
			)
			if not existing_bin:
				bin_doc = frappe.new_doc("Warehouse Bin")
				bin_doc.warehouse_rack = rack_name
				bin_doc.bin_number = f"B{bin_num}"
				bin_doc.bin_code = bin_code
				bin_doc.capacity = 100.0
				bin_doc.is_active = 1
				bin_doc.insert(ignore_permissions=True)
				bins[bin_code] = bin_doc.name
				frappe.logger().info(f"Created bin: {bin_code}")
			else:
				bins[bin_code] = existing_bin

	frappe.db.commit()
	return warehouse_name, zones, racks, bins


def create_sample_items_with_barcodes():
	"""Create sample items with barcodes for testing"""

	items_data = [
		{
			"item_code": "MAT-001",
			"item_name": "Steel Wire",
			"barcode": "8901234567890",
			"item_group": "Raw Materials"
		},
		{
			"item_code": "MAT-002",
			"item_name": "Copper Pipe",
			"barcode": "8901234567891",
			"item_group": "Raw Materials"
		},
		{
			"item_code": "MAT-003",
			"item_name": "Aluminum Sheet",
			"barcode": "8901234567892",
			"item_group": "Raw Materials"
		},
		{
			"item_code": "MAT-004",
			"item_name": "Plastic Pellets",
			"barcode": "8901234567893",
			"item_group": "Raw Materials"
		},
		{
			"item_code": "MAT-005",
			"item_name": "Rubber Components",
			"barcode": "8901234567894",
			"item_group": "Raw Materials"
		},
		{
			"item_code": "WIP-001",
			"item_name": "Semi-Finished Component A",
			"barcode": "8901234567895",
			"item_group": "Products"
		},
		{
			"item_code": "WIP-002",
			"item_name": "Semi-Finished Component B",
			"barcode": "8901234567896",
			"item_group": "Products"
		},
		{
			"item_code": "FIN-001",
			"item_name": "Finished Product A",
			"barcode": "8901234567897",
			"item_group": "Products"
		},
		{
			"item_code": "FIN-002",
			"item_name": "Finished Product B",
			"barcode": "8901234567898",
			"item_group": "Products"
		},
		{
			"item_code": "PKG-001",
			"item_name": "Cardboard Box",
			"barcode": "8901234567899",
			"item_group": "Products"
		},
	]

	created_items = []
	for item_data in items_data:
		if not frappe.db.exists("Item", item_data["item_code"]):
			item = frappe.new_doc("Item")
			item.item_code = item_data["item_code"]
			item.item_name = item_data["item_name"]
			item.item_group = item_data["item_group"]
			item.stock_uom = "Nos"
			# india_compliance (GST) requires an HSN/SAC code on every Item when
			# installed; 999900 is the standard catch-all "other" GST HSN code,
			# fine as a placeholder for demo/sample data.
			item.gst_hsn_code = "999900"
			item.insert(ignore_permissions=True)
			created_items.append(item_data["item_code"])
			frappe.logger().info(f"Created item: {item_data['item_code']}")

			# Add barcode
			barcode_exists = frappe.db.exists("Item Barcode", {"parent": item_data["item_code"]})
			if not barcode_exists:
				barcode = frappe.new_doc("Item Barcode")
				barcode.parent = item_data["item_code"]
				barcode.parenttype = "Item"
				barcode.parentfield = "barcodes"
				barcode.barcode = item_data["barcode"]
				barcode.insert(ignore_permissions=True)
				frappe.logger().info(f"Added barcode {item_data['barcode']} to {item_data['item_code']}")
		else:
			created_items.append(item_data["item_code"])

	frappe.db.commit()
	return created_items


def populate_initial_stock(warehouse_name, items=None, bins=None):
	"""Populate some initial stock in bins"""

	if items is None:
		items = frappe.db.get_list("Item", fields=["name"], limit=10)
	if bins is None:
		bins = frappe.db.get_list("Warehouse Bin", fields=["name"], limit=12)

	if not items or not bins:
		frappe.logger().warning("No items or bins available for stock population")
		return

	# Define stock allocation: which items go to which zone bins
	stock_allocation = {
		"MAT-001": 50,
		"MAT-002": 40,
		"MAT-003": 30,
		"MAT-004": 25,
		"MAT-005": 20,
		"WIP-001": 15,
		"WIP-002": 12,
		"FIN-001": 60,
		"FIN-002": 45,
		"PKG-001": 100,
	}

	for i, bin_record in enumerate(bins):
		if i < len(items):
			item_code = items[i]["name"]
			quantity = stock_allocation.get(item_code, 50 + (i * 10))

			try:
				update_bin_stock(bin_record["name"], item_code, quantity)
				frappe.logger().info(f"Added stock: {item_code} ({quantity} units) -> {bin_record['name']}")
			except Exception as e:
				frappe.logger().error(f"Error adding stock to bin {bin_record['name']}: {str(e)}")

	frappe.db.commit()


def run():
	"""Main function to run all fixture creation"""
	try:
		frappe.logger().info("Starting test fixture creation...")

		# Create warehouse structure
		warehouse_name, zones, racks, bins = create_sample_warehouse_structure()
		frappe.logger().info(f"Warehouse structure created: {warehouse_name}")
		frappe.logger().info(f"  - Zones: {len(zones)}")
		frappe.logger().info(f"  - Racks: {len(racks)}")
		frappe.logger().info(f"  - Bins: {len(bins)}")

		# Create items with barcodes
		items = create_sample_items_with_barcodes()
		frappe.logger().info(f"Items created: {len(items)}")

		# Populate initial stock
		populate_initial_stock(warehouse_name)
		frappe.logger().info("Initial stock populated")

		frappe.msgprint(
			f"Test fixtures created successfully!\n\n"
			f"Warehouse: {warehouse_name}\n"
			f"Zones: {len(zones)}\n"
			f"Racks: {len(racks)}\n"
			f"Bins: {len(bins)}\n"
			f"Items: {len(items)}",
			title="Fixtures Created"
		)

	except Exception as e:
		frappe.logger().error(f"Error creating fixtures: {str(e)}")
		frappe.throw(f"Error creating fixtures: {str(e)}")
