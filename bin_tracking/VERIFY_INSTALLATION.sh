#!/bin/bash

# Bin Tracking Installation Verification Script

echo "=========================================="
echo "Bin Tracking System - Verification Script"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check files
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        return 1
    fi
}

# Check directory
check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/"
        return 1
    fi
}

echo "Checking DocType files..."
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/warehouse_zone/warehouse_zone.json"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/warehouse_zone/warehouse_zone.py"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/warehouse_rack/warehouse_rack.json"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/warehouse_rack/warehouse_rack.py"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/warehouse_bin/warehouse_bin.json"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/warehouse_bin/warehouse_bin.py"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/bin_stock/bin_stock.json"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/bin_stock/bin_stock.py"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/bin_transfer/bin_transfer.json"
check_file "bin_tracking/bin_tracking/bin_tracking/doctype/bin_transfer/bin_transfer.py"

echo ""
echo "Checking www pages..."
check_file "bin_tracking/bin_tracking/www/bin-lookup.py"
check_file "bin_tracking/bin_tracking/www/bin-lookup.html"
check_file "bin_tracking/bin_tracking/www/bin-transfer.py"
check_file "bin_tracking/bin_tracking/www/bin-transfer.html"

echo ""
echo "Checking Python modules..."
check_file "bin_tracking/bin_tracking/api.py"
check_file "bin_tracking/bin_tracking/utils.py"
check_file "bin_tracking/bin_tracking/warehouse_events.py"
check_file "bin_tracking/bin_tracking/install.py"

echo ""
echo "Checking Frontend assets..."
check_file "bin_tracking/bin_tracking/public/css/bin_tracking.css"
check_file "bin_tracking/bin_tracking/public/js/bin_tracking.js"
check_file "bin_tracking/bin_tracking/public/js/item.js"
check_file "bin_tracking/bin_tracking/public/js/warehouse.js"

echo ""
echo "Checking app configuration..."
check_file "bin_tracking/__init__.py"
check_file "bin_tracking/bin_tracking/hooks.py"
check_file "bin_tracking/bin_tracking/modules.txt"
check_file "bin_tracking/setup.py"
check_file "bin_tracking/README.md"

echo ""
echo "Checking documentation..."
check_file "bin_tracking/TESTING.md"
check_file "bin_tracking/IMPLEMENTATION_SUMMARY.md"

echo ""
echo "Checking Docker updates..."
grep -q "bin_tracking" ../Dockerfile && echo -e "${GREEN}✓${NC} Dockerfile updated" || echo -e "${RED}✗${NC} Dockerfile not updated"

echo ""
echo "=========================================="
echo "Verification complete!"
echo "=========================================="
echo ""
echo "Installation instructions:"
echo "1. Build Docker image: docker build -t erpnext-bin-tracking ."
echo "2. Run container: docker run -d -p 8000:8000 -p 9000:9000 erpnext-bin-tracking"
echo "3. Access at: http://localhost:8000"
echo ""
echo "For testing, see bin_tracking/TESTING.md"
