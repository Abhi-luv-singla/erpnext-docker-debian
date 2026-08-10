frappe.ui.form.on("Item", {
	refresh: function (frm) {
		if (frm.doc.__islocal) {
			return;
		}

		frm.add_custom_button(
			__("Bin Stock Locations"),
			function () {
				frappe.call({
					method: "bin_tracking.api.get_item_stock_locations",
					args: { item_code: frm.doc.name },
					freeze: true,
					callback: function (r) {
						const data = r.message || {};
						if (!data.success) {
							frappe.msgprint({
								title: __("Bin Stock Locations"),
								indicator: "red",
								message: data.error || __("Could not load bin stock locations"),
							});
							return;
						}

						if (!data.locations || !data.locations.length) {
							frappe.msgprint({
								title: __("Bin Stock Locations"),
								indicator: "orange",
								message: __("This item is not currently stocked in any tracked bin."),
							});
							return;
						}

						const rows = data.locations
							.map(
								(loc) =>
									`<tr>
										<td>${frappe.utils.escape_html(loc.bin_code || loc.bin_number || "")}</td>
										<td>${frappe.utils.escape_html(loc.warehouse_rack || "")}</td>
										<td style="text-align:right">${frappe.format(loc.quantity, { fieldtype: "Float" })}</td>
										<td>${frappe.utils.escape_html(loc.uom || "")}</td>
									</tr>`
							)
							.join("");

						frappe.msgprint({
							title: __("Bin Stock Locations for {0}", [frm.doc.name]),
							indicator: "blue",
							message: `
								<table class="table table-bordered">
									<thead>
										<tr>
											<th>${__("Bin")}</th>
											<th>${__("Rack")}</th>
											<th>${__("Quantity")}</th>
											<th>${__("UOM")}</th>
										</tr>
									</thead>
									<tbody>${rows}</tbody>
								</table>
								<p><b>${__("Total")}:</b> ${frappe.format(data.total_quantity, { fieldtype: "Float" })}</p>
							`,
						});
					},
				});
			},
			__("View")
		);
	},
});
