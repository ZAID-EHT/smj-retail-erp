"""One admin-managed dropdown option.

A single master backs every option list the Retail ERP forms offer, so the
"add / delete the choices in this dropdown" button next to City, Business Nature,
Transport Method, Product Size, Product Material and Carpet Category is the same
page with a different type.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document

# The option types the forms know about. Kept here as well as in the Select's
# options so server code has one importable source rather than parsing metadata.
OPTION_TYPES = (
	"City",
	"Business Nature",
	"Transport Method",
	"Product Size",
	"Product Material",
	"Carpet Category",
)

# Which Customer / Item field each option type feeds. Used before deleting an
# option so a value already written onto records cannot silently disappear.
USAGE = {
	"City": ("Address", "city"),
	"Business Nature": ("Customer", "custom_business_nature"),
	"Transport Method": ("Customer", "custom_transport_method"),
	"Product Size": ("Item", "custom_product_size"),
	"Product Material": ("Item", "custom_product_material"),
	"Carpet Category": ("Item", "custom_carpet_category"),
}


class RetailOptionList(Document):
	def validate(self) -> None:
		self.option_value = (self.option_value or "").strip()
		if not self.option_value:
			frappe.throw(_("Option Value is required."), frappe.ValidationError)
		if self.option_type not in OPTION_TYPES:
			frappe.throw(_("Unsupported option type: {0}").format(self.option_type), frappe.ValidationError)
		# "::" is the name separator; a value containing it would produce a name
		# that no longer round-trips back to (type, value).
		if "::" in self.option_value:
			frappe.throw(_("Option Value cannot contain '::'."), frappe.ValidationError)
		duplicate = frappe.db.exists(
			"Retail Option List",
			{"option_type": self.option_type, "option_value": self.option_value, "name": ["!=", self.name]},
		)
		if duplicate:
			frappe.throw(
				_("{0} already has an option called {1}.").format(self.option_type, self.option_value),
				frappe.DuplicateEntryError,
			)

	def on_trash(self) -> None:
		"""Refuse to delete an option that records already carry.

		Deleting it would leave those records pointing at a value the form can no
		longer offer. Deactivating is the safe alternative and is what the admin
		page suggests.
		"""
		target = USAGE.get(self.option_type)
		if not target:
			return
		doctype, fieldname = target
		if not frappe.db.has_column(doctype, fieldname):
			return
		used = frappe.db.count(doctype, {fieldname: self.option_value})
		if used:
			frappe.throw(
				_("{0} is used by {1} {2} record(s). Untick Active instead of deleting it.").format(
					self.option_value, used, doctype
				),
				frappe.LinkExistsError,
			)
