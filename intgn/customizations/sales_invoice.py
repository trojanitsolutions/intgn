import frappe
from frappe import _
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

DEFAULT_PLATFORM = "ERPNext"

def create_custom_fields():
    custom_fields = {
        "Sales Invoice": [
            {
                "fieldname": "order_source_section",
                "fieldtype": "Section Break",
                "label": "Order Source / Platform Information",
                "insert_after": "po_date",
            },
            {
                "fieldname": "created_by_platform",
                "fieldtype": "Select",
                "label": "Created By Platform",
                "options": "ERPNext\nSnoonu\nTalabat",
                "default": DEFAULT_PLATFORM,
                "no_copy": 1,
                "in_standard_filter": 1,
                "insert_after": "order_source_section",
                "description": "Where this invoice/order originated",
            },
            {
                "fieldname": "order_source_column",
                "fieldtype": "Column Break",
                "insert_after": "created_by_platform",
            },
            {
                "fieldname": "talabat_order_id",
                "fieldtype": "Data",
                "label": "Talabat Order ID",
                "no_copy": 1,
                "search_index": 1,
                "in_standard_filter": 1,
                "in_global_search": 1,
                "insert_after": "order_source_column",
                "depends_on": "eval:doc.created_by_platform=='Talabat'",
                "description": "External order/reference ID received from Talabat.",
            },
            {
                "fieldname": "snoonu_order_id",
                "fieldtype": "Data",
                "label": "Snoonu Order ID",
                "no_copy": 1,
                "search_index": 1,
                "in_standard_filter": 1,
                "in_global_search": 1,
                "insert_after": "talabat_order_id",
                "depends_on": "eval:doc.created_by_platform=='Snoonu'",
                "description": "External order/reference ID received from Snoonu.",
            },
        ]
    }

    for doctype, fields in custom_fields.items():
        for field in fields:
            if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
                create_custom_field(doctype, field)
                frappe.db.commit()
                frappe.clear_cache(doctype=doctype)

def delete_custom_fields():
    custom_fields_to_delete = {
        "Sales Invoice": [
            "order_source_section", "created_by_platform", "order_source_column", "talabat_order_id", "snoonu_order_id",
        ]
    }

    for doctype, fields in custom_fields_to_delete.items():
        for field_name in fields:
            if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field_name}):
                frappe.delete_doc("Custom Field", f"{doctype}-{field_name}", ignore_missing=True)
                frappe.db.commit()
                frappe.clear_cache(doctype=doctype)

def id_fields(meta):
    """{platform: id fieldname}, derived from the Select options so no platform is hardcoded."""
    options = meta.get_field("created_by_platform").options.split("\n")
    return {p: f"{p.lower()}_order_id" for p in options if p and meta.has_field(f"{p.lower()}_order_id")}

def before_validate(doc, method=None):
    fields = id_fields(doc.meta)
    doc.created_by_platform = doc.created_by_platform or DEFAULT_PLATFORM
    for platform, fieldname in fields.items():
        value = (doc.get(fieldname) or "").strip()
        doc.set(fieldname, value if platform == doc.created_by_platform else "")

def validate(doc, method=None):
    fieldname = id_fields(doc.meta).get(doc.created_by_platform)
    if not fieldname or doc.is_return:
        return  # ERPNext has no external ID; returns may reuse the original order's ID

    label = _(doc.meta.get_label(fieldname))
    value = doc.get(fieldname)
    if not value:
        frappe.throw(_("{0} is required when Created By Platform is {1}").format(label, doc.created_by_platform))

    duplicate = frappe.db.get_value(
        "Sales Invoice", {fieldname: value, "docstatus": ["!=", 2], "is_return": 0, "name": ["!=", doc.name]}
    )
    if duplicate:
        frappe.throw(_("{0} {1} is already used on Sales Invoice {2}").format(label, value, duplicate))

def after_insert(doc, method=None):
    from intgn.api_logger import log_invoice_origin

    log_invoice_origin(doc)
