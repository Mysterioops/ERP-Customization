app_name = "erptask"
app_title = "Erptask"
app_publisher = "Adhi"
app_description = "Customization in ERPNEXT"
app_email = "adhi@gmail.com"
app_license = "mit"

required_apps = ["erpnext", "india_compliance"]

after_install = "erptask.install.after_install"

doctype_js = {
    "Purchase Invoice": "public/js/purchase_invoice.js"
}
doctype_list_js = {
    "Sales Invoice": "public/js/sales_invoice_list.js"
}
doc_events = {
    "Sales Invoice": {
        "before_insert": "erptask.overrides.sales_invoice.before_insert",
        "before_save": "erptask.overrides.sales_invoice.before_save",
        "validate": "erptask.install.validate_sales_invoice",
    },
    "Company": {
        "after_insert": "erptask.install.create_warehouses_for_company",
    }
}
