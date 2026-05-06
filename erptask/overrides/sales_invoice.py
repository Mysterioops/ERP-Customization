import frappe

    # =========================
    # Customization 1
    # =========================

def before_insert(doc, method=None):

    for item in doc.items:
        if item.sales_order: # If the item is linked to a Sales Order, fetch special instructions from the Sales Order and set it in the invoice header
            doc.custom_special_instructions_for_invoice = frappe.db.get_value(
                "Sales Order", item.sales_order, "custom_special_instructions_for_invoice"
            )
            break

    so_details = [item.so_detail for item in doc.items if item.so_detail] # List of all so_details used in the invoice
    if so_details: # If there are any so_details, fetch their product descriptions and set it in the invoice items
        rows = frappe.db.get_all(
            "Sales Order Item",
            filters={"name": ["in", so_details]},
            fields=["name", "custom_product_description"],
        )
        desc_map = {r.name: r.custom_product_description for r in rows} # Map of so_detail to product description
        for item in doc.items:
            if item.so_detail:
                item.custom_product_description = desc_map.get(item.so_detail)

    # =========================
    # Customization 2
    # =========================

EXPORT_GST_CATEGORIES = {"Deemed Export", "Overseas"}


def before_save(doc, method=None):
    # Only run on the very first save of a new invoice
    if not doc.is_new():
        return

    if not doc.customer or not doc.company:
        return

    # Read GST Category from Customer master (Tax tab)
    gst_category = frappe.db.get_value("Customer", doc.customer, "gst_category")

    if gst_category not in EXPORT_GST_CATEGORIES:
        return  # Not an export customer — do nothing

    # Read Export Account from Company master
    export_account = frappe.db.get_value(
        "Company", doc.company, "custom_export_customer_account"
    )

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

    # Fill income_account ONLY if user has not changed it
    for item in doc.items:

        if not item.income_account or item.income_account == item.get("default_income_account"):
            item.income_account = export_account
            updated_count += 1

    # Show message only if something was updated
    if updated_count:
        frappe.msgprint(
            msg=(
                f"Export Customer Account <b>{export_account}</b> auto-filled "
            ),
            title="Export Account Auto-Filled",
            indicator="blue",
            alert=True,
        )
