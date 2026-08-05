"""A category-wise price code and the running number behind every SKU.

The code (CCA, CCB, AAC …) carries the preset Wholesale / Department / Retail
prices a product of that code starts from, and owns its own counter, so choosing
CCA on the product form issues CCA 1, then CCA 2, and so on.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import cint, flt


class RetailPriceCode(Document):
	def validate(self) -> None:
		self.price_code = (self.price_code or "").strip().upper()
		if not self.price_code:
			frappe.throw(_("Price Code is required."), frappe.ValidationError)
		if not self.price_code.replace("-", "").replace("_", "").isalnum():
			frappe.throw(
				_("Price Code may only contain letters, digits, hyphens and underscores."),
				frappe.ValidationError,
			)
		if not frappe.db.exists("Item Group", {"name": self.category, "is_group": 0}):
			frappe.throw(_("{0} is not a selectable product category.").format(self.category),
			             frappe.ValidationError)
		for field in ("wholesale_price", "department_price", "retail_price"):
			if flt(self.get(field)) < 0:
				frappe.throw(_("{0} cannot be negative.").format(self.meta.get_label(field)),
				             frappe.ValidationError)

	def on_trash(self) -> None:
		used = frappe.db.count("Item", {"custom_price_code": self.name})
		if used:
			frappe.throw(
				_("{0} is used by {1} product(s). Untick Active instead of deleting it.").format(
					self.name, used),
				frappe.LinkExistsError,
			)


def peek_next_sku(price_code: str) -> str | None:
	"""The SKU the next product of this code would get -- without consuming it.

	Preview only. Two people previewing at the same time see the same number; the
	number is only settled by `issue_sku` at save time.
	"""
	if not price_code:
		return None
	current = frappe.db.get_value("Retail Price Code", price_code, "current_sequence")
	if current is None:
		return None
	return f"{price_code} {cint(current) + 1}"


def issue_sku(price_code: str) -> str:
	"""Consume the next number for this code and return the SKU.

	`for_update` takes a row lock so two products saved at the same moment cannot
	be handed the same number -- the second waits, re-reads, and gets the next one.
	"""
	if not frappe.db.exists("Retail Price Code", price_code):
		frappe.throw(_("Price Code {0} does not exist.").format(price_code), frappe.ValidationError)
	current = cint(frappe.db.get_value("Retail Price Code", price_code, "current_sequence",
	                                   for_update=True))
	nxt = current + 1
	frappe.db.set_value("Retail Price Code", price_code, "current_sequence", nxt,
	                    update_modified=False)
	return f"{price_code} {nxt}"
