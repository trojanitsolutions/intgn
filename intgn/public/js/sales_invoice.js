// Shows only the external order ID matching Created By Platform; fields follow the <platform>_order_id convention.
(function () {
	function set_platform_fields(frm, clear) {
		const platforms = (frm.fields_dict.created_by_platform.df.options || "").split("\n").filter(Boolean);
		platforms.forEach((platform) => {
			const fieldname = `${platform.toLowerCase()}_order_id`;
			if (!frm.fields_dict[fieldname]) return;
			const active = frm.doc.created_by_platform === platform;
			frm.toggle_display(fieldname, active);
			if (!active && clear && frm.doc[fieldname]) frm.set_value(fieldname, "");
		});
	}

	frappe.ui.form.on("Sales Invoice", {
		refresh(frm) {
			set_platform_fields(frm);
		},
		created_by_platform(frm) {
			set_platform_fields(frm, true);
		},
	});
})();
