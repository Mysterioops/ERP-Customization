import frappe


def create_sales_invoice_workflow():
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
			frappe.get_doc(
				{
					"doctype": "Workflow State",
					"workflow_state_name": state,
					"style": style,
				}
			).insert(ignore_permissions=True)
		else:
			frappe.db.set_value("Workflow State", state, "style", style)

	for action in ["Request Approval", "Approve", "Reject", "Resubmit"]:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc(
				{
					"doctype": "Workflow Action Master",
					"workflow_action_name": action,
				}
			).insert(ignore_permissions=True)

	workflow = frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": "Sales Invoice Approval",
			"document_type": "Sales Invoice",
			"is_active": 1,
			"override_status": 0,
			"workflow_state_field": "workflow_state",
			"states": [
				{"state": "Draft", "doc_status": "0", "allow_edit": "Sales User", "style": "Inverse"},
				{
					"state": "Pending Approval",
					"doc_status": "0",
					"allow_edit": "Sales Manager",
					"style": "Warning",
				},
				{"state": "Approved", "doc_status": "1", "allow_edit": "Sales Manager", "style": "Success"},
				{"state": "Rejected", "doc_status": "0", "allow_edit": "Sales User", "style": "Danger"},
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
		}
	)
	workflow.insert(ignore_permissions=True)

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
		frappe.get_doc(
			{
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
			}
		).insert(ignore_permissions=True)


def validate_sales_invoice(doc, method=None):
	if doc.docstatus == 1 and doc.get("workflow_state") not in ("Approved", None):
		frappe.throw("Sales Invoice must be in Approved state before submission.")
