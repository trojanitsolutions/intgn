import frappe

from intgn.customizations.sales_invoice import id_fields


def log_invoice_origin(doc, response=None, error=None):
	"""Write one API Logger row for a Sales Invoice. Never raises: logging must not block invoicing."""
	try:
		fieldname = id_fields(doc.meta).get(doc.created_by_platform)
		frappe.get_doc({
			"doctype": "API Logger",
			"sales_invoice": doc.name,
			"created_by_platform": doc.created_by_platform,
			"external_order_id": doc.get(fieldname) if fieldname else None,
			"created_by": frappe.session.user,
			"status": "Failed" if error else "Success",
			"response": frappe.as_json(error or response) if (error or response) else None,
		}).insert(ignore_permissions=True)
	except Exception:
		frappe.log_error(title="API Logger write failed")
