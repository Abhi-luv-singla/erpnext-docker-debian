/**
 * Bin Tracking Scanner Module
 * Handles barcode/QR code scanner events, validation, and processing
 */

// ==================== Scanner Configuration ====================
const SCANNER_CONFIG = {
	timeout: 5000,                          // Scanner input timeout (ms)
	debounceTime: 300,                      // Debounce time for scanner events (ms)
	minLength: 3,                           // Minimum barcode length
	maxLength: 128,                         // Maximum barcode length
	scannerKeyTimeout: 50,                  // Max time between scanner keystrokes (ms)
	duplicateScanWindow: 2000,              // Window to detect duplicate scans (ms)
	pattern: /^[A-Z0-9\-\.]+$/,             // Alphanumeric, hyphens, dots
	barcodePatterns: {
		code128: /^[0-9A-Za-z\-\.]+$/,      // Code 128 format
		upc: /^[0-9]{12,13}$/,              // UPC format (12-13 digits)
		ean: /^[0-9]{13,14}$/,              // EAN format (13-14 digits)
		qr: /^.*$/,                         // QR code (any content)
		custom: /^[A-Z0-9\-]+$/              // Custom format (alphanumeric + hyphens)
	},
	enableAutoFocus: true,                  // Auto-focus scanner input
	enableDuplicateDetection: true,         // Detect duplicate scans
	enableValidation: true,                 // Validate barcode format
};

// Scanner state management
const SCANNER_STATE = {
	isScanning: false,
	lastScanValue: null,
	lastScanTime: null,
	lastScanTimestamp: null,
	scanBuffer: '',
	scanStartTime: null,
	scanHistory: [],
	activeInput: null,
	registeredHandlers: [],
	errors: [],
	stats: {
		totalScans: 0,
		validScans: 0,
		invalidScans: 0,
		duplicateScans: 0,
		errors: 0
	}
};

// ==================== Validation Functions ====================

/**
 * Validate barcode format and content
 * @param {string} barcode - Barcode to validate
 * @param {string} format - Expected format (code128, upc, ean, qr, custom)
 * @returns {object} Validation result
 */
function validateBarcode(barcode, format = 'custom') {
	const result = {
		valid: false,
		error: null,
		warnings: [],
		barcode: barcode,
		format: format
	};

	// Check if barcode is empty
	if (!barcode || barcode.trim().length === 0) {
		result.error = 'Barcode cannot be empty';
		return result;
	}

	const trimmedBarcode = barcode.trim();

	// Check length
	if (trimmedBarcode.length < SCANNER_CONFIG.minLength) {
		result.error = `Barcode too short (minimum ${SCANNER_CONFIG.minLength} characters)`;
		return result;
	}

	if (trimmedBarcode.length > SCANNER_CONFIG.maxLength) {
		result.error = `Barcode too long (maximum ${SCANNER_CONFIG.maxLength} characters)`;
		return result;
	}

	// Validate against format pattern
	const pattern = SCANNER_CONFIG.barcodePatterns[format] || SCANNER_CONFIG.barcodePatterns.custom;
	if (!pattern.test(trimmedBarcode)) {
		result.error = `Barcode format invalid for type: ${format}`;
		return result;
	}

	// Additional format-specific validation
	if (format === 'upc' && !/^[0-9]{12,13}$/.test(trimmedBarcode)) {
		result.error = 'UPC barcode must be 12 or 13 digits';
		return result;
	}

	if (format === 'ean' && !/^[0-9]{13,14}$/.test(trimmedBarcode)) {
		result.error = 'EAN barcode must be 13 or 14 digits';
		return result;
	}

	result.valid = true;
	result.barcode = trimmedBarcode;
	return result;
}

/**
 * Validate QR code data
 * @param {string} qrData - QR code data to validate
 * @returns {object} Validation result
 */
function validateQRCode(qrData) {
	const result = {
		valid: false,
		error: null,
		data: qrData
	};

	if (!qrData || qrData.trim().length === 0) {
		result.error = 'QR code data cannot be empty';
		return result;
	}

	try {
		const trimmed = qrData.trim();

		// QR codes can contain various data types
		// Validate basic structure
		if (trimmed.length > SCANNER_CONFIG.maxLength) {
			result.error = `QR code data exceeds maximum length (${SCANNER_CONFIG.maxLength} characters)`;
			return result;
		}

		result.valid = true;
		result.data = trimmed;
		return result;
	} catch (e) {
		result.error = 'Invalid QR code data: ' + e.message;
		return result;
	}
}

/**
 * Validate quantity input
 * @param {string|number} quantity - Quantity value
 * @returns {object} Validation result
 */
function validateQuantity(quantity) {
	const result = {
		valid: false,
		error: null,
		value: null
	};

	if (!quantity && quantity !== 0) {
		result.error = 'Quantity is required';
		return result;
	}

	const qty = parseFloat(quantity);

	if (isNaN(qty)) {
		result.error = 'Quantity must be a valid number';
		return result;
	}

	if (qty <= 0) {
		result.error = 'Quantity must be greater than 0';
		return result;
	}

	if (!Number.isFinite(qty)) {
		result.error = 'Quantity must be a finite number';
		return result;
	}

	result.valid = true;
	result.value = qty;
	return result;
}

/**
 * Validate bin code format
 * @param {string} binCode - Bin code to validate
 * @returns {object} Validation result
 */
function validateBinCode(binCode) {
	return validateBarcode(binCode, 'custom');
}

/**
 * Check if scan is duplicate
 * @param {string} scanValue - Scanned value
 * @returns {boolean} True if duplicate
 */
function isDuplicateScan(scanValue) {
	if (!SCANNER_CONFIG.enableDuplicateDetection) {
		return false;
	}

	const now = Date.now();
	const window = SCANNER_CONFIG.duplicateScanWindow;

	// Check against last scan
	if (SCANNER_STATE.lastScanValue === scanValue &&
		now - SCANNER_STATE.lastScanTime < window) {
		SCANNER_STATE.stats.duplicateScans++;
		return true;
	}

	return false;
}

// ==================== Formatting Functions ====================

/**
 * Format quantity with 2 decimal places
 * @param {number} qty - Quantity to format
 * @returns {string} Formatted quantity
 */
function formatQuantity(qty) {
	try {
		const num = parseFloat(qty);
		return isNaN(num) ? '0.00' : num.toFixed(2);
	} catch (e) {
		return '0.00';
	}
}

/**
 * Format barcode for display
 * @param {string} barcode - Barcode to format
 * @returns {string} Formatted barcode
 */
function formatBarcode(barcode) {
	if (!barcode) return '';
	return barcode.trim().toUpperCase();
}

/**
 * Add checksum to UPC barcode (if applicable)
 * @param {string} barcode - UPC barcode
 * @returns {string} Barcode with checksum
 */
function addUPCChecksum(barcode) {
	if (!barcode || barcode.length < 11) return barcode;

	const digits = barcode.slice(0, -1);
	let sum = 0;

	for (let i = 0; i < digits.length; i++) {
		const digit = parseInt(digits[i]);
		sum += (i % 2 === 0) ? digit * 3 : digit;
	}

	const checksum = (10 - (sum % 10)) % 10;
	return digits + checksum;
}

// ==================== Notification Functions ====================

/**
 * Show notification message
 * @param {string} message - Message to display
 * @param {string} type - Notification type (info, success, warning, danger)
 * @param {number} duration - Duration in milliseconds
 */
function showNotification(message, type = 'info', duration = 5000) {
	try {
		if (typeof frappe !== 'undefined' && frappe.msgprint) {
			// Use Frappe's built-in notification if available
			const indicatorType = type === 'danger' ? 'red' :
								   type === 'warning' ? 'orange' :
								   type === 'success' ? 'green' : 'blue';
			frappe.show_alert({ message: message, indicator: indicatorType });
		} else {
			// Fallback to Bootstrap alert
			const alertClass = `alert-${type === 'danger' ? 'danger' : type}`;
			const notification = $(`
				<div class="alert ${alertClass} alert-dismissible fade show" role="alert">
					${message}
					<button type="button" class="close" data-dismiss="alert" aria-label="Close">
						<span aria-hidden="true">&times;</span>
					</button>
				</div>
			`);

			$('body').prepend(notification);

			if (duration > 0) {
				setTimeout(() => {
					notification.fadeOut(() => notification.remove());
				}, duration);
			}
		}
	} catch (e) {
		console.error('Error showing notification:', e);
	}
}

/**
 * Show validation error
 * @param {string} fieldName - Field name
 * @param {string} error - Error message
 */
function showValidationError(fieldName, error) {
	const message = `${fieldName}: ${error}`;
	showNotification(message, 'warning', 3000);
	SCANNER_STATE.errors.push({ field: fieldName, error: error, timestamp: new Date() });
	SCANNER_STATE.stats.errors++;
}

// ==================== Scanner Event Handling ====================

/**
 * Initialize scanner event listeners on an input element
 * @param {string|HTMLElement} inputSelector - Input selector or element
 * @param {function} onScan - Callback when valid scan is detected
 * @param {object} options - Additional options
 */
function initScannerInput(inputSelector, onScan, options = {}) {
	const element = typeof inputSelector === 'string' ?
					document.querySelector(inputSelector) :
					inputSelector;

	if (!element) {
		console.error('Scanner input element not found:', inputSelector);
		return false;
	}

	const config = Object.assign({
		format: 'custom',
		enableValidation: true,
		enableDuplicateDetection: true,
		autoFocus: true,
		clearOnScan: true,
		onError: null
	}, options);

	let scanBuffer = '';
	let scanStartTime = null;

	/**
	 * Process scanner input
	 */
	function processScan(value) {
		SCANNER_STATE.stats.totalScans++;

		// Validate barcode
		if (config.enableValidation) {
			const validation = validateBarcode(value, config.format);
			if (!validation.valid) {
				SCANNER_STATE.stats.invalidScans++;
				if (config.onError) {
					config.onError(validation.error);
				} else {
					showValidationError('Scan', validation.error);
				}
				return false;
			}
		}

		// Check for duplicate
		if (config.enableDuplicateDetection && isDuplicateScan(value)) {
			console.warn('Duplicate scan detected:', value);
			showNotification('Duplicate scan detected', 'warning', 2000);
			return false;
		}

		// Update state
		SCANNER_STATE.lastScanValue = value;
		SCANNER_STATE.lastScanTime = Date.now();
		SCANNER_STATE.lastScanTimestamp = new Date();
		SCANNER_STATE.stats.validScans++;

		// Add to history
		SCANNER_STATE.scanHistory.push({
			value: value,
			timestamp: new Date(),
			format: config.format
		});

		// Keep history limited to last 100 scans
		if (SCANNER_STATE.scanHistory.length > 100) {
			SCANNER_STATE.scanHistory.shift();
		}

		// Call user callback
		if (onScan) {
			onScan(value);
		}

		// Clear input if configured
		if (config.clearOnScan) {
			element.value = '';
		}

		// Re-focus if configured
		if (config.autoFocus) {
			element.focus();
		}

		return true;
	}

	/**
	 * Handle Enter key / scanner terminator
	 */
	function handleScanComplete() {
		if (scanBuffer.length === 0) return;

		const value = scanBuffer.trim();
		scanBuffer = '';
		scanStartTime = null;

		processScan(value);
	}

	// Keyboard event listener
	element.addEventListener('keypress', function(e) {
		// Detect Enter key (scanner terminator)
		if (e.key === 'Enter' || e.which === 13) {
			e.preventDefault();
			handleScanComplete();
		}
	});

	// Handle pasted content (for virtual scanners, mobile, etc.)
	element.addEventListener('paste', function(e) {
		e.preventDefault();
		const pastedText = (e.clipboardData || window.clipboardData).getData('text');
		element.value = '';
		if (pastedText) {
			processScan(pastedText);
		}
	});

	// Clear scan state on blur
	element.addEventListener('blur', function() {
		scanBuffer = '';
		scanStartTime = null;
	});

	// Focus event
	element.addEventListener('focus', function() {
		SCANNER_STATE.activeInput = element;
	});

	// Store reference
	SCANNER_STATE.activeInput = element;
	SCANNER_STATE.registeredHandlers.push({
		element: element,
		selector: inputSelector,
		handler: processScan,
		config: config
	});

	return true;
}

/**
 * Process scanner input with debouncing
 * @param {string} value - Scanned value
 * @param {function} callback - Callback function
 */
function processScannerInput(value, callback) {
	if (!value || value.trim().length === 0) {
		return;
	}

	// Validate
	const validation = validateBarcode(value);
	if (!validation.valid) {
		showValidationError('Scanner', validation.error);
		if (callback) callback(false, validation.error);
		return;
	}

	// Check for duplicates
	if (isDuplicateScan(value)) {
		showNotification('Duplicate scan detected', 'warning');
		if (callback) callback(false, 'Duplicate scan');
		return;
	}

	// Update state
	SCANNER_STATE.lastScanValue = value;
	SCANNER_STATE.lastScanTime = Date.now();
	SCANNER_STATE.stats.validScans++;

	if (callback) {
		callback(true, value);
	}
}

/**
 * Global keypress listener for scanner detection
 */
document.addEventListener('keypress', function(e) {
	// Only process if active input is a barcode/scanner field
	const activeElement = document.activeElement;
	if (!activeElement) return;

	const id = activeElement.id || '';
	const name = activeElement.name || '';
	const classList = activeElement.classList || [];

	// Check if element is a scanner input
	const isScannerInput = id.includes('barcode') || id.includes('qr') ||
						   id.includes('scanner') || id.includes('scan') ||
						   name.includes('barcode') || name.includes('qr') ||
						   Array.from(classList).some(c =>
							   c.includes('barcode') || c.includes('qr') || c.includes('scanner')
						   );

	if (!isScannerInput) return;

	// Handle Enter key
	if (e.key === 'Enter' || e.which === 13) {
		e.preventDefault();
		const event = new CustomEvent('barcodeScanned', {
			detail: {
				value: activeElement.value,
				timestamp: new Date(),
				element: activeElement
			}
		});
		activeElement.dispatchEvent(event);
	}
});

// ==================== Scanner State Management ====================

/**
 * Get scanner state
 * @returns {object} Current scanner state
 */
function getScannerState() {
	return Object.assign({}, SCANNER_STATE);
}

/**
 * Get scanner statistics
 * @returns {object} Scanner statistics
 */
function getScannerStats() {
	return Object.assign({}, SCANNER_STATE.stats);
}

/**
 * Reset scanner state
 */
function resetScannerState() {
	SCANNER_STATE.lastScanValue = null;
	SCANNER_STATE.lastScanTime = null;
	SCANNER_STATE.lastScanTimestamp = null;
	SCANNER_STATE.scanBuffer = '';
	SCANNER_STATE.scanStartTime = null;
	SCANNER_STATE.errors = [];
}

/**
 * Reset scanner statistics
 */
function resetScannerStats() {
	SCANNER_STATE.stats = {
		totalScans: 0,
		validScans: 0,
		invalidScans: 0,
		duplicateScans: 0,
		errors: 0
	};
}

/**
 * Get scan history
 * @param {number} limit - Maximum number of entries to return
 * @returns {array} Scan history
 */
function getScanHistory(limit = 10) {
	const history = SCANNER_STATE.scanHistory;
	return limit > 0 ? history.slice(-limit) : history;
}

/**
 * Clear scan history
 */
function clearScanHistory() {
	SCANNER_STATE.scanHistory = [];
}

/**
 * Get recent errors
 * @param {number} limit - Maximum number of errors to return
 * @returns {array} Recent errors
 */
function getRecentErrors(limit = 10) {
	const errors = SCANNER_STATE.errors;
	return limit > 0 ? errors.slice(-limit) : errors;
}

// ==================== Utility Functions ====================

/**
 * Create test scan for debugging
 * @param {string} value - Test value
 * @param {string} format - Barcode format
 */
function createTestScan(value, format = 'custom') {
	const validation = validateBarcode(value, format);
	console.log('Test Scan:', {
		value: value,
		format: format,
		validation: validation
	});
	return validation;
}

/**
 * Generate sample barcode
 * @param {string} format - Barcode format
 * @returns {string} Sample barcode
 */
function generateSampleBarcode(format = 'custom') {
	const samples = {
		code128: 'BIN-001-' + Date.now().toString().slice(-6),
		upc: Math.random().toString().slice(2, 14),
		ean: Math.random().toString().slice(2, 15),
		qr: 'QR-' + Date.now().toString().slice(-8),
		custom: 'BIN-' + Math.random().toString(36).substr(2, 9).toUpperCase()
	};
	return samples[format] || samples.custom;
}

/**
 * Log scanner activity
 * @param {string} action - Action name
 * @param {object} data - Additional data
 */
function logScannerActivity(action, data = {}) {
	const entry = {
		timestamp: new Date().toISOString(),
		action: action,
		data: data,
		state: getScannerStats()
	};
	console.log('[Scanner]', entry);
}

// ==================== Exports ====================

// Export for Node.js/CommonJS
if (typeof module !== 'undefined' && module.exports) {
	module.exports = {
		// Configuration
		SCANNER_CONFIG,
		SCANNER_STATE,

		// Validation
		validateBarcode,
		validateQRCode,
		validateQuantity,
		validateBinCode,
		isDuplicateScan,

		// Formatting
		formatQuantity,
		formatBarcode,
		addUPCChecksum,

		// Notifications
		showNotification,
		showValidationError,

		// Scanner Events
		initScannerInput,
		processScannerInput,

		// State Management
		getScannerState,
		getScannerStats,
		resetScannerState,
		resetScannerStats,
		getScanHistory,
		clearScanHistory,
		getRecentErrors,

		// Utilities
		createTestScan,
		generateSampleBarcode,
		logScannerActivity
	};
}

// Export for Frappe/Browser
if (typeof frappe !== 'undefined') {
	frappe.ui.form.BinTrackingScanner = {
		initScannerInput,
		validateBarcode,
		validateQRCode,
		validateQuantity,
		validateBinCode,
		formatBarcode,
		formatQuantity,
		showNotification,
		showValidationError,
		getScannerState,
		getScannerStats,
		getScanHistory,
		resetScannerState,
		logScannerActivity
	};
}
