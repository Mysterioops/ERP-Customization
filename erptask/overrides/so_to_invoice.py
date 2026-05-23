import frappe


def before_insert(doc, method=None):
	for item in doc.items:
		if item.sales_order:
			doc.custom_special_instructions_for_invoice = frappe.db.get_value(
				"Sales Order", item.sales_order, "custom_special_instructions_for_invoice"
			)
			break

	so_details = [item.so_detail for item in doc.items if item.so_detail]
	if so_details:
		rows = frappe.db.get_all(
			"Sales Order Item",
			filters={"name": ["in", so_details]},
			fields=["name", "custom_product_description"],
		)
		desc_map = {r.name: r.custom_product_description for r in rows}
		for item in doc.items:
			if item.so_detail:
				item.custom_product_description = desc_map.get(item.so_detail)
