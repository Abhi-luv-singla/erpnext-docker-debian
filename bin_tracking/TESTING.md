# Bin Tracking System - Testing Guide

## Overview
This document describes how to test the Bin Tracking system in ERPNext.

## Prerequisites
- ERPNext v16 running with bin_tracking app installed
- Access to the web interface at http://localhost:8000
- Administrator or Stock Manager role

## Test Scenarios

### 1. Setup Test Data

Before running any tests, create the warehouse structure and items.

**Steps:**
1. Go to ERPNext home
2. Create a new document: "Warehouse Zone"
   - Warehouse: Select your warehouse
   - Zone Name: "Raw Material Zone"
   - Zone Type: "Raw Material"
   - Save

3. Create "Warehouse Rack"
   - Warehouse Zone: Select the zone created above
   - Rack Code: "A"
   - Rack Name: "Rack A"
   - Save

4. Create "Warehouse Bin"
   - Warehouse Rack: Select rack created above
   - Bin Number: "1"
   - Bin Code: "BIN-A-1"
   - Capacity: 100
   - Save
   - (QR code will be auto-generated)

5. Create Items with Barcodes
   - Go to Item list
   - Create new Item: "MAT-001", name: "Test Material"
   - In Item Barcode section, add: "8901234567890"
   - Save

### 2. Bin Lookup Test

Test scanning QR codes to view bin contents.

**Steps:**
1. Navigate to `/bin-lookup` page
2. Scan the QR code (or manually enter: "BIN-A-1")
3. Verify bin information appears
4. Expected result: Bin details displayed (should be empty initially)

### 3. Bin Transfer Test

Test the complete material transfer workflow.

**Prerequisites:**
- At least 2 bins created (e.g., BIN-A-1, BIN-A-2)
- At least 1 item with barcode (e.g., MAT-001)
- Stock added to source bin

**Steps:**
1. First, add stock to BIN-A-1:
   - Navigate to "Bin Stock" doctype
   - Create new record
   - Select Bin: BIN-A-1
   - Select Item: MAT-001
   - Set Quantity: 50
   - Save

2. Navigate to `/bin-transfer` page

3. Follow the steps:
   - **Step 1:** Scan item barcode (enter: 8901234567890)
   - Expected: Item details appear (MAT-001 - Test Material)
   
   - **Step 2:** Scan source bin QR (or enter: BIN-A-1)
   - Expected: Source bin info displays
   
   - **Step 3:** Scan destination bin QR (or enter: BIN-A-2)
   - Expected: Destination bin info displays
   
   - **Step 4:** Enter quantity (e.g., 20)
   - Click "Complete Transfer"
   - Expected: Success message with transfer ID

4. **Verify the transfer:**
   - Check Bin Stock for MAT-001 in BIN-A-1: Should be 30 (50-20)
   - Check Bin Stock for MAT-001 in BIN-A-2: Should be 20
   - Open Bin Transfer doctype, find the created transfer record
   - Verify status is "Submitted"

### 4. Negative Test Cases

#### Test 4.1: Insufficient Stock
**Steps:**
1. Try to transfer 100 units when only 30 available
2. Expected: Error message "Insufficient quantity in source bin"

#### Test 4.2: Invalid Barcode
**Steps:**
1. On `/bin-transfer` page, enter invalid barcode
2. Expected: Error message "Item not found"

#### Test 4.3: Invalid Bin
**Steps:**
1. On `/bin-transfer` page, enter invalid bin QR code
2. Expected: Error message "Bin not found"

#### Test 4.4: Same Source and Destination
**Steps:**
1. Try to transfer from BIN-A-1 to BIN-A-1
2. Expected: Error message "Source and destination bins cannot be the same"

### 5. Database Verification Tests

Run these checks in the database to verify data integrity.

```sql
-- Check if warehouse zone was created
SELECT * FROM `tabWarehouse Zone` WHERE is_deleted=0;

-- Check if bins exist
SELECT name, bin_number, warehouse_rack FROM `tabWarehouse Bin` WHERE is_deleted=0;

-- Check stock tracking
SELECT warehouse_bin, item_code, quantity FROM `tabBin Stock` WHERE is_deleted=0;

-- Check transfer history
SELECT name, item_code, source_bin, destination_bin, quantity, docstatus 
FROM `tabBin Transfer` WHERE is_deleted=0;
```

## Test Data Creation Script

To automatically create test data, run this in the console:

```python
from bin_tracking.fixtures.sample_data import create_sample_warehouse_structure, create_sample_items_with_barcodes

# Create warehouse structure
warehouse, zones, racks, bins = create_sample_warehouse_structure()

# Create sample items
create_sample_items_with_barcodes()

print("Test data created successfully!")
```

## Mobile Testing

The system is designed for mobile/tablet use with barcode scanners.

**Test on Mobile:**
1. Access ERPNext on mobile device or tablet
2. Navigate to `/bin-transfer`
3. Use camera barcode scanner (if available) or manual input
4. Verify:
   - Text input is large enough (font-size 16px)
   - No horizontal scroll
   - Buttons are touch-friendly
   - Workflow is clear on small screens

## Performance Testing

Test with large datasets:

1. Create 100+ bins
2. Add stock to 50+ bins
3. Perform 20+ transfers
4. Verify:
   - Page load time < 2 seconds
   - Transfer processing < 1 second
   - No JavaScript errors in console

## Browser Compatibility

Test on:
- Chrome (Latest)
- Firefox (Latest)
- Safari (Latest)
- Mobile browsers (Chrome Mobile, Safari Mobile)

## Cleanup

To clean up test data:

```python
import frappe

# Delete test transfers
frappe.db.delete_doc_if_exists("Bin Transfer", limit=100)

# Delete test stock
frappe.db.delete_doc_if_exists("Bin Stock", limit=100)

# Delete test bins
frappe.db.delete_doc_if_exists("Warehouse Bin", limit=100)

# Delete test racks
frappe.db.delete_doc_if_exists("Warehouse Rack", limit=100)

# Delete test zones
frappe.db.delete_doc_if_exists("Warehouse Zone", limit=100)
```

## Troubleshooting

### Pages not loading
- Clear browser cache
- Rebuild assets: `bench build`
- Check console for JavaScript errors

### QR codes not scanning
- Ensure QR code image is clear
- Use a barcode scanner app for testing
- Check QR code generation in Warehouse Bin document

### Stock not updating
- Check Bin Stock records exist
- Verify Transfer document is submitted (not draft)
- Check user permissions for Bin Stock/Bin Transfer

## Success Criteria

✅ All test scenarios pass
✅ No database errors
✅ Stock levels accurate after transfers
✅ Transfer history logged correctly
✅ Mobile interface responsive
✅ Performance acceptable

## Known Limitations

- Single warehouse testing (multi-warehouse in future)
- Manual QR code entry for testing (real scanners in production)
- No real-time inventory sync with main stock ledger (planned)
