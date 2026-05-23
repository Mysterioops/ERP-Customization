import frappe


def before_uninstall():
	remove_custom_fields()
	remove_custom_warehouses()
	remove_sales_invoice_workflow()
	remove_custom_permissions()
	frappe.db.commit()
	frappe.clear_cache()


def remove_custom_fields():
	frappe.db.delete("Custom Field", {"module": "Erptask"})


def remove_custom_warehouses():
	warehouse_names = ["Main Store", "Raw Materials", "Finished Goods"]
	for company in frappe.get_all("Company", pluck="name"):
		for name in warehouse_names:
			warehouse = frappe.db.get_value(
				"Warehouse", {"warehouse_name": name, "company": company}
			)
			if warehouse:
				try:
					frappe.delete_doc("Warehouse", warehouse, ignore_permissions=True, force=True)
				except Exception:
					frappe.log_error(f"Could not delete warehouse '{name}' for {company} — it may have stock entries.")


def remove_sales_invoice_workflow():
	if frappe.db.exists("Workflow", "Sales Invoice Approval"):
		frappe.delete_doc("Workflow", "Sales Invoice Approval", ignore_permissions=True, force=True)


def remove_custom_permissions():
	frappe.db.delete(
		"Custom DocPerm",
		{"parent": "Sales Invoice", "role": "Sales User", "permlevel": 0},
	)
