import frappe


def after_install():
	create_custom_fields()
	create_custom_warehouses()
	create_sales_invoice_workflow()


# ─── Custom Fields ────────────────────────────────────────────────────────────

CUSTOM_FIELDS = {
	"Sales Order": [
		{"fieldname": "custom_special_instructions_for_invoice", "label": "Special Instructions",
		 "fieldtype": "Small Text", "insert_after": "customer"},
	],
	"Sales Invoice": [
		{"fieldname": "custom_special_instructions_for_invoice", "label": "Special Instructions",
		 "fieldtype": "Small Text", "insert_after": "customer"},
	],
	"Sales Order Item": [
		{"fieldname": "custom_product_description", "label": "Product Description",
		 "fieldtype": "Text", "insert_after": "item_name"},
	],
	"Sales Invoice Item": [
		{"fieldname": "custom_product_description", "label": "Product Description",
		 "fieldtype": "Text", "insert_after": "item_name"},
	],
	"Company": [
		{"fieldname": "custom_export_customer_account", "label": "Export Customer Account",
		 "fieldtype": "Link", "options": "Account", "insert_after": "default_receivable_account"},
	],
	"Supplier": [
		{"fieldname": "custom_max_purchase", "label": "Max Purchase",
		 "fieldtype": "Currency", "insert_after": "supplier_name"},
	],
	"Purchase Invoice": [
		{"fieldname": "custom_purchase_limit_indicator", "label": "Purchase Limit Indicator",
		 "fieldtype": "HTML", "insert_after": "supplier"},
	],
}


def create_custom_fields(): # This function can be safely re-run without creating duplicate fields
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as _create
	_create(CUSTOM_FIELDS, ignore_validate=True)
	frappe.db.commit()
	frappe.clear_cache()


## ───────────────────────────────────────────────────────────────

## Customizations 4

## ───────────────────────────────────────────────────────────────

WAREHOUSES = [
	{"warehouse_name": "Main Store", "is_group": 0},
	{"warehouse_name": "Raw Materials", "is_group": 0},
	{"warehouse_name": "Finished Goods", "is_group": 0},
]


def create_custom_warehouses():
	# This function creates the custom warehouses for all existing companies.
	for company in frappe.get_all("Company", pluck="name"):
		_create_warehouses_for(company)
	frappe.db.commit()


def create_warehouses_for_company(doc, method=None):
	# This function is triggered by the "after_insert" event of the Company doctype. It creates the custom warehouses for the newly created company.
	_create_warehouses_for(doc.name)
	frappe.db.commit()


def _create_warehouses_for(company):
	# This function can be safely re-run for the same company without creating duplicate warehouses, as it checks for existence before creating.
	parent_warehouse = frappe.db.get_value(
		"Warehouse", {"warehouse_name": "All Warehouses", "company": company}
	)

	for wh in WAREHOUSES: #
		if frappe.db.exists("Warehouse", {"warehouse_name": wh["warehouse_name"], "company": company}):
			continue

		frappe.get_doc({
			"doctype": "Warehouse",
			"warehouse_name": wh["warehouse_name"],
			"is_group": wh["is_group"],
			"company": company,
			"parent_warehouse": parent_warehouse,
		}).insert(ignore_permissions=True, ignore_mandatory=True)



## ───────────────────────────────────────────────────────────────

## Customizations 5

## ───────────────────────────────────────────────────────────────

def create_sales_invoice_workflow():
	# Idempotent: skip if an active workflow already exists for Sales Invoice
	if frappe.db.exists("Workflow", {"document_type": "Sales Invoice", "is_active": 1}):
		return

	state_styles = {
		"Draft": "Inverse",
		"Pending Approval": "Warning",
		"Approved": "Success",
		"Rejected": "Danger",
	}

	for state, style in state_styles.items():
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc({
				"doctype": "Workflow State",
				"workflow_state_name": state,
				"style": style,
			}).insert(ignore_permissions=True)
		else:
			frappe.db.set_value("Workflow State", state, "style", style)
	# Workflow Actions are standard and can be reused across workflows, so we check by name only
	for action in ["Request Approval", "Approve", "Reject", "Resubmit"]:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({
				"doctype": "Workflow Action Master",
				"workflow_action_name": action,
			}).insert(ignore_permissions=True)

	workflow = frappe.get_doc({
		"doctype": "Workflow",
		"workflow_name": "Sales Invoice Approval",
		"document_type": "Sales Invoice",
		"is_active": 1,
		"override_status": 0,
		"workflow_state_field": "workflow_state",
		"states": [
			{"state": "Draft",            "doc_status": "0", "allow_edit": "Sales User",    "style": "Inverse"},
			{"state": "Pending Approval", "doc_status": "0", "allow_edit": "Sales Manager", "style": "Warning"},
			{"state": "Approved",         "doc_status": "1", "allow_edit": "Sales Manager", "style": "Success"},
			{"state": "Rejected",         "doc_status": "0", "allow_edit": "Sales User",    "style": "Danger"},
		],
		"transitions": [
			{
				"state": "Draft",
				"action": "Request Approval",
				"next_state": "Pending Approval",
				"allowed": "Sales User",
			},
			{
				"state": "Pending Approval",
				"action": "Approve",
				"next_state": "Approved",
				"allowed": "Sales Manager",
			},
			{
				"state": "Pending Approval",
				"action": "Reject",
				"next_state": "Rejected",
				"allowed": "Sales Manager",
			},
			{
				"state": "Rejected",
				"action": "Resubmit",
				"next_state": "Pending Approval",
				"allowed": "Sales User",
			},
		],
	})
	workflow.insert(ignore_permissions=True) # Insert the workflow

	set_sales_invoice_permissions()
	frappe.db.commit()


def set_sales_invoice_permissions():
	existing = frappe.db.get_value(
		"Custom DocPerm",
		{"parent": "Sales Invoice", "role": "Sales User", "permlevel": 0},
		"name",
	)

	if existing:
		frappe.db.set_value("Custom DocPerm", existing, "submit", 0)
	else:
		frappe.get_doc({
			"doctype": "Custom DocPerm",
			"parent": "Sales Invoice",
			"parenttype": "DocType",
			"parentfield": "permissions",
			"role": "Sales User",
			"permlevel": 0,
			"read": 1,
			"write": 1,
			"create": 1,
			"submit": 0,
		}).insert(ignore_permissions=True)


def validate_sales_invoice(doc, method=None):
	if doc.docstatus == 1 and doc.get("workflow_state") not in ("Approved", None):
		frappe.throw("Sales Invoice must be in Approved state before submission.")
