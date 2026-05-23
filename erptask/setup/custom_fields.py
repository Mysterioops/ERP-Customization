import frappe

CUSTOM_FIELDS = {
	"Sales Order": [
		{
			"fieldname": "custom_special_instructions_for_invoice",
			"label": "Special Instructions",
			"fieldtype": "Small Text",
			"insert_after": "customer",
			"module": "Erptask",
		},
	],
	"Sales Invoice": [
		{
			"fieldname": "custom_special_instructions_for_invoice",
			"label": "Special Instructions",
			"fieldtype": "Small Text",
			"insert_after": "customer",
			"module": "Erptask",
		},
	],
	"Sales Order Item": [
		{
			"fieldname": "custom_product_description",
			"label": "Product Description",
			"fieldtype": "Text",
			"insert_after": "item_name",
			"module": "Erptask",
		},
	],
	"Sales Invoice Item": [
		{
			"fieldname": "custom_product_description",
			"label": "Product Description",
			"fieldtype": "Text",
			"insert_after": "item_name",
			"module": "Erptask",
		},
	],
	"Company": [
		{
			"fieldname": "custom_export_customer_account",
			"label": "Export Customer Account",
			"fieldtype": "Link",
			"options": "Account",
			"insert_after": "default_receivable_account",
			"module": "Erptask",
		},
	],
	"Supplier": [
		{
			"fieldname": "custom_max_purchase",
			"label": "Max Purchase",
			"fieldtype": "Currency",
			"insert_after": "supplier_name",
			"module": "Erptask",
		},
	],
	"Purchase Invoice": [
		{
			"fieldname": "custom_purchase_limit_indicator",
			"label": "Purchase Limit Indicator",
			"fieldtype": "HTML",
			"insert_after": "supplier",
			"module": "Erptask",
		},
	],
}


def create_custom_fields():
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields as _create

	_create(CUSTOM_FIELDS, ignore_validate=True)
	frappe.db.commit()
	frappe.clear_cache()
