import frappe

from intgn.customizations.sales_invoice import create_custom_fields


def execute():
	create_custom_fields()  # patches run before after_migrate, so the column may not exist yet
	frappe.db.sql(
		"update `tabSales Invoice` set created_by_platform='ERPNext' where ifnull(created_by_platform,'')=''"
	)
