# Bin Tracking System for ERPNext

A comprehensive Frappe application for ERPNext that enables advanced warehouse bin tracking with QR code and barcode support.

## 🎯 Overview

The Bin Tracking System provides hierarchical warehouse management with the following structure:

```
Warehouse
└── Zone (Raw Material, WIP, Packaging, Rejection, etc.)
    └── Rack (A, B, C, D, etc.)
        └── Bin (1, 2, 3, 4, 5, etc.)
            └── Stock (Item → Quantity)
```

Each bin is automatically assigned a QR code for quick scanning and identification.

## ✨ Key Features

- **Hierarchical Warehouse Structure**: Organize warehouses into zones, racks, and bins
- **Automatic QR Code Generation**: Every bin gets a unique QR code for scanning
- **Barcode Item Tracking**: Items can be tracked using barcodes
- **Real-Time Stock Tracking**: Track inventory at the bin level
- **Quick Material Transfer**: Move items between bins by scanning barcodes and QR codes
- **Transfer History**: Complete audit trail of all material movements
- **Mobile-Friendly Interface**: Responsive design for tablet and mobile use
- **Multi-Zone Support**: Handle different material zones (raw materials, WIP, packaging, rejection)

## 📦 Installation

### Docker Installation (Recommended)

The app is pre-configured in the Docker setup. It will be installed automatically when the Docker image is built.

### Manual Installation

```bash
# In your Frappe bench environment
bench get-app bin_tracking https://github.com/frappe/bin_tracking.git
bench --site site1.local install-app bin_tracking
```

## 🚀 Quick Start

### 1. Create Warehouse Structure

1. **Create a Zone** (Inventory → Warehouse Zone)
   - Select your Warehouse
   - Name: "Raw Material Zone"
   - Type: "Raw Material"
   - Save

2. **Create a Rack** (Inventory → Warehouse Rack)
   - Select the Zone you created
   - Code: "A"
   - Name: "Rack A"
   - Save

3. **Create Bins** (Inventory → Warehouse Bin)
   - Select the Rack
   - Bin Number: "1"
   - Capacity: 100 units
   - Save (QR code auto-generated)

### 2. Add Items with Barcodes

1. Create an Item with barcode:
   - Code: "MAT-001"
   - Name: "Steel Wire"
   - In Item Barcode section, add: "8901234567890"
   - Save

### 3. Add Stock to Bins

1. **Bin Stock** (Inventory → Bin Stock)
   - Select Bin: "BIN-001"
   - Select Item: "MAT-001"
   - Quantity: 100
   - Save

### 4. Use Scanning Features

#### Bin Lookup (View Contents)
- Navigate to: `/bin-lookup`
- Scan or enter bin QR code
- View all items and quantities in that bin

#### Bin Transfer (Move Items)
- Navigate to: `/bin-transfer`
- Scan item barcode
- Scan source bin QR code
- Scan destination bin QR code
- Enter quantity to transfer
- Submit

## 📋 DocTypes Included

### Setup DocTypes
- **Warehouse Zone** - Define zones within a warehouse
- **Warehouse Rack** - Define racks within a zone
- **Warehouse Bin** - Define individual bins (auto-generates QR codes)
- **Bin Stock** - Track items and quantities in bins

### Transaction DocTypes
- **Bin Transfer** - Record material movements between bins

## 🌐 API Endpoints

All whitelisted methods live in a single canonical module, `bin_tracking.api`:

```python
# Scan an item barcode
GET /api/method/bin_tracking.api.scan_item_barcode?barcode=XXX

# Scan a bin QR code / bin code (returns bin details + contents)
GET /api/method/bin_tracking.api.scan_bin_barcode?barcode=XXX

# Get full item details (incl. all registered barcodes)
GET /api/method/bin_tracking.api.get_item_details?item_code=XXX

# Get every bin where an item currently has stock
GET /api/method/bin_tracking.api.get_item_stock_locations?item_code=XXX

# Get all item stock contents of a bin
GET /api/method/bin_tracking.api.get_bin_stock_details?warehouse_bin=XXX

# Get active bins within a zone (destination picker)
GET /api/method/bin_tracking.api.get_available_bins?warehouse_zone=XXX

# Validate a transfer before committing (fast-fail UX check only —
# the authoritative, lock-protected check runs in BinTransfer.validate/on_submit)
POST /api/method/bin_tracking.api.validate_transfer
# Arguments: item_code, source_bin, destination_bin, quantity

# Process a bin-to-bin transfer (creates + submits a Bin Transfer)
POST /api/method/bin_tracking.api.process_transfer
# Arguments: item_code, source_bin, destination_bin, quantity, remarks (optional)

# Process multiple transfers in one call
POST /api/method/bin_tracking.api.batch_transfer
# Arguments: transfers_data (JSON array of the process_transfer arguments above)

# Get transfer history (all filters optional)
GET /api/method/bin_tracking.api.get_transfer_history?item_code=XXX&source_bin=YYY&destination_bin=ZZZ&limit=50

# Get a single transfer's details
GET /api/method/bin_tracking.api.get_transfer_details?transfer_id=XXX
```

All methods require a logged-in session (no `allow_guest`) and return `{"success": bool, ...}`.

## 🌱 Sample / Test Data

To populate a Faridabad warehouse with 4 zones, 3 racks per zone, 5 bins per rack, 10 sample items with barcodes, and initial stock, run:

```bash
bench --site site1.local execute bin_tracking.commands.create_test_fixtures.run_all
```

This calls into `bin_tracking/bin_tracking/fixtures/sample_data.py` directly — it is idempotent (safe to re-run) and requires Administrator privileges. This is the only supported way to load sample data; there is no `bench migrate`-based fixture import for this app.

## 🧪 Testing

See [TESTING.md](./TESTING.md) for comprehensive testing guide.

Quick test:
1. Navigate to `/bin-lookup` and scan a bin
2. Navigate to `/bin-transfer` and complete a transfer
3. Verify stock levels updated correctly

## 📱 Mobile Usage

The system is optimized for mobile and tablet use:

- Large touch-friendly buttons
- Clear step-by-step workflow
- Barcode scanner integration
- No horizontal scrolling
- Responsive design for all screen sizes

## 🔒 Permissions

- **System Manager** - Full access
- **Stock Manager** - Full access to zones, racks, bins, and transfers
- **Stock User** - Read-only access

## ⚙️ Configuration

### Warehouse Zone Types
- Raw Material
- Work in Progress
- Packaging
- Rejection
- Other (Custom)

### QR Code Settings
QR codes are automatically generated for each bin. Customize in Warehouse Bin doctype.

## 🐛 Troubleshooting

### QR codes not displaying
- Check browser console for errors
- Ensure qrcode and Pillow Python packages are installed
- Rebuild assets: `bench build`

### Barcode scanner not working
- Ensure barcode is in correct format (alphanumeric)
- Test with manual entry first
- Verify item barcode exists in Item master

### Stock not updating after transfer
- Check Bin Transfer document is submitted (not draft)
- Verify user has Stock Manager role
- Check for error messages in Bin Transfer form

### Pages not loading
- Clear browser cache
- Check that bin_tracking app is installed: `bench list-apps`
- Restart bench: `bench start`

## 📊 Database Queries

Useful queries for reporting:

```sql
-- All stock by bin
SELECT wb.name as bin, wi.item_code, wi.item_name, bs.quantity
FROM `tabBin Stock` bs
JOIN `tabWarehouse Bin` wb ON bs.warehouse_bin = wb.name
JOIN `tabItem` wi ON bs.item_code = wi.item_code
ORDER BY wb.name, wi.item_code;

-- Total transfers
SELECT COUNT(*) as total_transfers, SUM(quantity) as total_quantity
FROM `tabBin Transfer`
WHERE docstatus = 1;

-- Recent transfers
SELECT name, item_code, source_bin, destination_bin, quantity, transfer_date
FROM `tabBin Transfer`
WHERE docstatus = 1
ORDER BY transfer_date DESC
LIMIT 10;
```

## 🔄 Integration with ERPNext

The system tracks bin-level stock separately. For full integration with ERPNext's stock ledger:

1. Bin transfers create transfer records (audit trail)
2. Consider creating Stock Entries for period-end reconciliation
3. Use Bin Stock reports for inventory planning

## 🚀 Future Enhancements

- [ ] Real-time sync with ERPNext Stock Ledger
- [ ] Multi-warehouse transfers
- [ ] Automated reorder point management
- [ ] Advanced reporting and analytics
- [ ] Barcode label generation
- [ ] Mobile app (native iOS/Android)
- [ ] Integration with weight/dimension sensors

## 📝 License

MIT

## 👥 Contributors

- Abhilav Singla (Initial development)

## 📞 Support

For issues, suggestions, or contributions, please open an issue on the repository.

## 📚 Documentation

- [Testing Guide](./TESTING.md) - Comprehensive testing instructions

---

**Version**: 0.0.1  
**Last Updated**: 2024-08-06  
**Compatibility**: ERPNext v16, Frappe Framework
