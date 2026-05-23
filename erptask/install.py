from erptask.setup.custom_fields import create_custom_fields
from erptask.setup.warehouses import create_custom_warehouses
from erptask.setup.workflow import create_sales_invoice_workflow


def after_install():
	create_custom_fields()
	create_custom_warehouses()
	create_sales_invoice_workflow()
