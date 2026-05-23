import frappe

EXPORT_GST_CATEGORIES = {"Deemed Export", "Overseas"}


def before_save(doc, method=None):
	if not doc.is_new():
		return

	if not doc.customer or not doc.company:
		return

	gst_category = frappe.db.get_value("Customer", doc.customer, "gst_category")

	if gst_category not in EXPORT_GST_CATEGORIES:
		return

	export_account = frappe.db.get_value("Company", doc.company, "custom_export_customer_account")

	if not export_account:
		frappe.msgprint(
			msg=(
				f"Export Customer Account is not configured for company <b>{doc.company}</b>. "
				"Please set it under <b>Company → Export Customer Account</b>."
			),
			title="Export Account Not Configured",
			indicator="orange",
			alert=True,
		)
		return

	updated_count = 0

	for item in doc.items:
		if not item.income_account or item.income_account == item.get("default_income_account"):
			item.income_account = export_account
			updated_count += 1

	if updated_count:
		frappe.msgprint(
			msg=(f"Export Customer Account <b>{export_account}</b> auto-filled "),
			title="Export Account Auto-Filled",
			indicator="blue",
			alert=True,
		)
