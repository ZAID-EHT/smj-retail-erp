"""Exact Customer quick-create/edit workflow.

Atomic: creates the Customer through the standard controller, then a linked standard
Address and Contact (via Dynamic Link), the transport / BR / business-nature fields,
the price category (selling Price List), and the credit classification (custom_credit_type
+ standard credit_limits child + custom_credit_days). Any failure rolls back.

Visible business fields: Customer, Address, Contact No, WhatsApp No, Account Dept No,
Transport Detail, Transport Method, BR No, Business Nature, Price Category, Payment
Type, Credit Limit, Credit Days, Created Date.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt

CREDIT_TYPE_FIELD = "custom_credit_type"
CREDIT = "Credit Customer"
NON_CREDIT = "Non-Credit Customer"

ALLOWED_KEYS = {
	"customer_name", "address", "address_line2", "city", "state", "pincode", "country",
	"contact_no", "whatsapp_no", "same_whatsapp", "accounts_department_no",
	"transport_detail", "transport_method", "br_no", "business_nature",
	"price_category", "payment_type", "credit_limit", "credit_days",
}
# Visible "Payment Type" -> backing custom_credit_type value.
PAYMENT_TYPE_MAP = {"Credit": CREDIT, "Non-Credit": NON_CREDIT}


def _clean(values) -> dict:
	data = frappe.parse_json(values) if isinstance(values, str) else values
	if not isinstance(data, dict):
		frappe.throw(_("Invalid customer details."), frappe.ValidationError)
	unknown = set(data) - ALLOWED_KEYS
	if unknown:
		frappe.throw(_("Unsupported field: {0}").format(", ".join(sorted(unknown))), frappe.ValidationError)
	return data


def _validate_price_list(name: str) -> str:
	name = str(name or "").strip() or "Retail Price List"
	row = frappe.db.get_value("Price List", {"name": name, "enabled": 1}, ["name", "selling"], as_dict=True)
	if not row:
		frappe.throw(_("Price Category {0} is not available.").format(name), frappe.ValidationError)
	if not row.selling:
		frappe.throw(_("Price Category must be a selling Price List."), frappe.ValidationError)
	return row["name"]


@frappe.whitelist(methods=["GET"])
def find_duplicate_customers(customer_name: str) -> dict:
	"""Warn about likely duplicates before creating."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	name = str(customer_name or "").strip()
	if not name:
		return {"candidates": []}
	rows = frappe.get_list("Customer", filters={"customer_name": ["like", f"%{name[:60]}%"]},
	                       fields=["name", "customer_name"], limit_page_length=5)
	return {"candidates": rows}


@frappe.whitelist(methods=["POST"])
def create_customer(values: dict | str, name: str | None = None):
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)
	data = _clean(values)

	editing = bool(name)
	if editing:
		if not frappe.db.exists("Customer", name):
			frappe.throw(_("Customer not found."), frappe.DoesNotExistError)
		doc = frappe.get_doc("Customer", name)
		if not frappe.has_permission("Customer", "write", doc=doc):
			frappe.throw(_("You cannot edit this customer."), frappe.PermissionError)
	else:
		if not frappe.has_permission("Customer", "create"):
			frappe.throw(_("You cannot create customers."), frappe.PermissionError)
		doc = frappe.new_doc("Customer")
		doc.customer_type = "Company"
		doc.customer_group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name")[0]
		doc.territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name")[0]

	customer_name = str(data.get("customer_name") or "").strip()
	if not customer_name:
		frappe.throw(_("Customer is required."), frappe.ValidationError)
	doc.customer_name = customer_name

	price_list = _validate_price_list(data.get("price_category"))
	doc.default_price_list = price_list

	# Payment Type -> credit classification.
	payment_type = str(data.get("payment_type") or "").strip()
	credit_type = PAYMENT_TYPE_MAP.get(payment_type)
	if payment_type and not credit_type:
		frappe.throw(_("Payment Type must be Credit or Non-Credit."), frappe.ValidationError)
	is_credit = credit_type == CREDIT
	credit_limit = flt(data.get("credit_limit"))
	credit_days = cint(data.get("credit_days"))
	if is_credit:
		if credit_limit <= 0:
			frappe.throw(_("Credit customers require a Credit Limit greater than zero."), frappe.ValidationError)
		if credit_days < 0:
			frappe.throw(_("Credit Days cannot be negative."), frappe.ValidationError)
	if credit_type:
		doc.set(CREDIT_TYPE_FIELD, credit_type)
	doc.custom_credit_days = credit_days if is_credit else 0

	# Safe Credit -> Non-Credit conversion: refuse if outstanding exists.
	if editing and not is_credit and doc.get(CREDIT_TYPE_FIELD) == CREDIT:
		from erpnext.selling.doctype.customer.customer import get_customer_outstanding
		company = frappe.defaults.get_global_default("company")
		outstanding = flt(get_customer_outstanding(doc.name, company)) if company else 0
		if outstanding > 0:
			frappe.throw(_("Cannot switch to Non-Credit while {0} has outstanding balance {1}.").format(
				doc.name, outstanding), frappe.ValidationError)

	doc.mobile_no = str(data.get("contact_no") or "").strip() or None
	same = cint(data.get("same_whatsapp"))
	doc.custom_whatsapp_no = (doc.mobile_no if same else str(data.get("whatsapp_no") or "").strip()) or None
	doc.custom_accounts_department_no = str(data.get("accounts_department_no") or "").strip() or None
	doc.custom_transport_method = str(data.get("transport_method") or "").strip() or None
	doc.custom_transport_detail = str(data.get("transport_detail") or "").strip() or None
	doc.custom_br_no = str(data.get("br_no") or "").strip() or None
	doc.custom_business_nature = str(data.get("business_nature") or "").strip() or None

	if editing:
		doc.save()
	else:
		doc.insert()

	# Credit limit -> standard credit_limits child (per company), no duplicate rows.
	_apply_credit_limit(doc, credit_limit if is_credit else 0)
	# Address + Contact (standard, linked), no duplicates.
	_upsert_address(doc, data)
	_upsert_contact(doc, data)

	return {"name": doc.name, "customer": doc.customer_name, "route": f"/sales/customers/{doc.name}"}


def _apply_credit_limit(doc, limit: float) -> None:
	company = frappe.defaults.get_global_default("company") or (
		frappe.get_all("Company", pluck="name", limit_page_length=1) or [None])[0]
	if not company:
		return
	doc.reload()
	rows = [r for r in doc.get("credit_limits", []) if r.company == company]
	if limit > 0:
		row = rows[0] if rows else doc.append("credit_limits", {"company": company})
		row.credit_limit = limit
	elif rows:
		for r in rows:
			doc.get("credit_limits").remove(r)
	doc.save()


def _upsert_address(doc, data: dict) -> None:
	line1 = str(data.get("address") or "").strip()
	if not line1:
		return
	# Find an existing linked address of this app's making, else create one.
	existing = frappe.get_all(
		"Dynamic Link", filters={"link_doctype": "Customer", "link_name": doc.name, "parenttype": "Address"},
		pluck="parent", limit_page_length=1)
	if existing:
		addr = frappe.get_doc("Address", existing[0])
	else:
		addr = frappe.new_doc("Address")
		addr.address_title = doc.customer_name
		addr.address_type = "Billing"
		addr.is_primary_address = 1
		addr.append("links", {"link_doctype": "Customer", "link_name": doc.name})
	# Only overwrite a subfield when the caller supplied it, so an edit that omits
	# (say) city does not blank an existing mandatory value.
	def _set(field, key):
		val = str(data.get(key) or "").strip()
		if val:
			setattr(addr, field, val)
	addr.address_line1 = line1
	_set("address_line2", "address_line2")
	_set("city", "city")
	_set("state", "state")
	_set("pincode", "pincode")
	if not addr.country:
		addr.country = str(data.get("country") or "").strip() or frappe.db.get_default("country") or "Sri Lanka"
	addr.save(ignore_permissions=False) if existing else addr.insert()


def _upsert_contact(doc, data: dict) -> None:
	phone = str(data.get("contact_no") or "").strip()
	if not phone and not str(data.get("whatsapp_no") or "").strip():
		return
	existing = frappe.get_all(
		"Dynamic Link", filters={"link_doctype": "Customer", "link_name": doc.name, "parenttype": "Contact"},
		pluck="parent", limit_page_length=1)
	if existing:
		contact = frappe.get_doc("Contact", existing[0])
	else:
		contact = frappe.new_doc("Contact")
		contact.first_name = doc.customer_name
		contact.is_primary_contact = 1
		contact.append("links", {"link_doctype": "Customer", "link_name": doc.name})
	if phone:
		contact.set("phone_nos", [])
		contact.append("phone_nos", {"phone": phone, "is_primary_mobile_no": 1, "is_primary_phone": 1})
		contact.mobile_no = phone
	contact.save(ignore_permissions=False) if existing else contact.insert()


@frappe.whitelist(methods=["GET"])
def get_customer(name: str) -> dict:
	if not frappe.has_permission("Customer", "read", doc=name):
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	doc = frappe.get_doc("Customer", name)
	addr = frappe.get_all("Dynamic Link", filters={"link_doctype": "Customer", "link_name": name, "parenttype": "Address"}, pluck="parent", limit_page_length=1)
	address = frappe.get_doc("Address", addr[0]) if addr else None
	credit_type = doc.get(CREDIT_TYPE_FIELD)
	company = frappe.defaults.get_global_default("company")
	credit_limit = flt(next((r.credit_limit for r in doc.get("credit_limits", []) if r.company == company), 0))
	return {
		"name": doc.name, "customer_name": doc.customer_name,
		"address": address.address_line1 if address else None,
		"city": address.city if address else None,
		"contact_no": doc.mobile_no, "whatsapp_no": doc.custom_whatsapp_no,
		"accounts_department_no": doc.custom_accounts_department_no,
		"transport_method": doc.custom_transport_method, "transport_detail": doc.custom_transport_detail,
		"br_no": doc.custom_br_no, "business_nature": doc.custom_business_nature,
		"price_category": doc.default_price_list,
		"payment_type": "Credit" if credit_type == CREDIT else ("Non-Credit" if credit_type else None),
		"credit_limit": credit_limit, "credit_days": cint(doc.custom_credit_days),
		"created": str(doc.creation),
	}
