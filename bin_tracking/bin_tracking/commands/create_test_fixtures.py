#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create test fixtures for the bin tracking system.

Usage:
    bench execute bin_tracking.commands.create_test_fixtures.run_all
"""

import frappe
from bin_tracking.fixtures.sample_data import (
    create_sample_warehouse_structure,
    create_sample_items_with_barcodes,
    populate_initial_stock,
)


def run_all():
    """Run all fixture creation functions"""
    import sys

    if not frappe.session.user == "Administrator":
        frappe.throw("This command requires Administrator privileges")

    try:
        print("Creating test fixtures...")

        # Create warehouse structure
        print("\n1. Creating warehouse structure...")
        warehouse_name, zones, racks, bins = create_sample_warehouse_structure()
        print(f"   - Warehouse: {warehouse_name}")
        print(f"   - Zones: {list(zones.keys())}")
        print(f"   - Total Racks: {len(racks)}")
        print(f"   - Total Bins: {len(bins)}")

        # Create items with barcodes
        print("\n2. Creating sample items with barcodes...")
        items = create_sample_items_with_barcodes()
        print(f"   - Items created: {len(items)}")
        for item in items:
            print(f"     - {item}")

        # Populate initial stock
        print("\n3. Populating initial stock...")
        populate_initial_stock(warehouse_name)
        print("   - Initial stock populated")

        print("\nTest fixtures created successfully!")
        print("\nSummary:")
        print(f"  Warehouse: {warehouse_name}")
        print(f"  Zones: {len(zones)}")
        print(f"  Racks: {len(racks)}")
        print(f"  Bins: {len(bins)}")
        print(f"  Items: {len(items)}")

    except Exception as e:
        print(f"Error: {str(e)}")
        frappe.log_error(str(e), "Test Fixture Creation Error")
        sys.exit(1)
