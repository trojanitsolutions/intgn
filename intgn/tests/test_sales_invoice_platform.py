import frappe
from frappe.tests import IntegrationTestCase

from intgn.customizations.sales_invoice import before_validate, validate


def _si(platform=None, **ids):
	return frappe.get_doc({"doctype": "Sales Invoice", "name": "new", "created_by_platform": platform, **ids})


class TestSalesInvoicePlatform(IntegrationTestCase):
	def test_default_and_clearing(self):
		doc = _si(None, talabat_order_id="X", snoonu_order_id="Y")
		before_validate(doc)
		self.assertEqual(doc.created_by_platform, "ERPNext")
		self.assertFalse(doc.talabat_order_id or doc.snoonu_order_id)

	def test_platform_keeps_only_own_id(self):
		doc = _si("Talabat", talabat_order_id=" TAL-1 ", snoonu_order_id="SN-1")
		before_validate(doc)
		self.assertEqual(doc.talabat_order_id, "TAL-1")
		self.assertFalse(doc.snoonu_order_id)

	def test_id_required(self):
		doc = _si("Snoonu")
		before_validate(doc)
		self.assertRaises(frappe.ValidationError, validate, doc)
