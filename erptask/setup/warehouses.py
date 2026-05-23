import frappe

WAREHOUSES = [
	{"warehouse_name": "Main Store", "is_group": 0},
	{"warehouse_name": "Raw Materials", "is_group": 0},
	{"warehouse_name": "Finished Goods", "is_group": 0},
]


def create_custom_warehouses():
	for company in frappe.get_all("Company", pluck="name"):
		_create_warehouses_for(company)
	frappe.db.commit()


def create_warehouses_for_company(doc, method=None):
	_create_warehouses_for(doc.name)
	frappe.db.commit()


def _create_warehouses_for(company):
	parent_warehouse = frappe.db.get_value(
		"Warehouse", {"warehouse_name": "All Warehouses", "company": company}
	)

	for wh in WAREHOUSES:
		if frappe.db.exists("Warehouse", {"warehouse_name": wh["warehouse_name"], "company": company}):
			continue

		frappe.get_doc(
			{
				"doctype": "Warehouse",
				"warehouse_name": wh["warehouse_name"],
				"is_group": wh["is_group"],
				"company": company,
				"parent_warehouse": parent_warehouse,
			}
		).insert(ignore_permissions=True, ignore_mandatory=True)
