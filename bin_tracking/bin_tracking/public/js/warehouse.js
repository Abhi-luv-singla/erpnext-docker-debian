frappe.ui.form.on("Warehouse", {
	refresh: function (frm) {
		if (frm.doc.__islocal) {
			return;
		}

		frm.add_custom_button(
			__("Zones && Bins"),
			function () {
				frappe.set_route("list", "warehouse-zone", { warehouse: frm.doc.name });
			},
			__("View")
		);

		frm.add_custom_button(
			__("Bin Lookup"),
			function () {
				window.open("/bin-lookup", "_blank");
			},
			__("View")
		);
	},
});
