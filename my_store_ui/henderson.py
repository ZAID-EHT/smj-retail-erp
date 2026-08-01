"""Henderson strategic-alignment analysis.

Deliberately isolated from the operational modules. Nothing here reads or writes
pricing, stock, reservations, warehouses or any sales/purchase document -- it only
reads and writes Henderson Assessment records.

Editing is restricted to management/administrator roles through the DocType's own
permissions; every endpoint re-checks on the server so the frontend guard is never
the only control.
"""

from __future__ import annotations

import json

import frappe
from frappe import _
from frappe.utils import cint, nowdate

from my_store_ui.my_store_ui.doctype.henderson_assessment.henderson_assessment import (
	DOMAINS,
	MAX_SCORE,
)

DOCTYPE = "Henderson Assessment"


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _require_read() -> None:
	_require_login()
	if not frappe.has_permission(DOCTYPE, "read"):
		frappe.throw(_("You do not have access to the Henderson analysis."), frappe.PermissionError)


def _require_write() -> None:
	_require_login()
	if not frappe.has_permission(DOCTYPE, "write"):
		frappe.throw(
			_("Only management roles can edit the Henderson analysis."), frappe.PermissionError
		)


def _gap(row) -> int:
	return max(cint(row.get("target_score")) - cint(row.get("current_score")), 0)


@frappe.whitelist(methods=["GET"])
def get_henderson_analysis(company: str | None = None, name: str | None = None):
	"""The current assessment for a company, with gaps and priorities derived."""
	_require_read()
	company = (company or "").strip() or frappe.defaults.get_user_default("Company") \
		or frappe.db.get_default("company")

	if name:
		if not frappe.has_permission(DOCTYPE, "read", doc=name):
			frappe.throw(_("You do not have access to this assessment."), frappe.PermissionError)
		doc = frappe.get_doc(DOCTYPE, name)
	else:
		# get_list applies User Permissions; get_all would bypass them.
		rows = frappe.get_list(
			DOCTYPE, filters={"company": company} if company else {},
			fields=["name"], order_by="assessment_date desc, modified desc", limit=1,
		)
		doc = frappe.get_doc(DOCTYPE, rows[0]["name"]) if rows else None

	can_edit = bool(frappe.has_permission(DOCTYPE, "write"))
	history = frappe.get_list(
		DOCTYPE, filters={"company": company} if company else {},
		fields=["name", "assessment_date", "status", "modified", "modified_by"],
		order_by="assessment_date desc", limit=12,
	)

	if not doc:
		return {
			"company": company, "assessment": None, "domains": [], "history": history,
			"can_edit": can_edit, "domain_options": list(DOMAINS), "max_score": MAX_SCORE,
			"summary": {"average_current": 0, "average_target": 0, "total_gap": 0,
			            "priority_areas": []},
		}

	# Present every domain, including ones never assessed, so a gap cannot hide.
	domains = []
	by_domain = {row.domain: row for row in doc.get("domains") or []}
	for domain in DOMAINS:
		row = by_domain.get(domain)
		entry = {
			"domain": domain,
			"current_score": cint(row.current_score) if row else 0,
			"target_score": cint(row.target_score) if row else 0,
			"priority": (row.priority if row else "Medium") or "Medium",
			"notes": (row.notes if row else "") or "",
			"assessed": bool(row),
		}
		entry["gap"] = _gap(entry)
		domains.append(entry)

	assessed = [d for d in domains if d["assessed"]]
	count = len(assessed) or 1
	priority_areas = sorted(
		[d for d in domains if d["gap"] > 0],
		key=lambda d: (-d["gap"], d["domain"]),
	)[:3]

	return {
		"company": company,
		"assessment": {
			"name": doc.name, "company": doc.company,
			"assessment_date": str(doc.assessment_date), "status": doc.status,
			"summary_notes": doc.summary_notes or "",
			"modified": str(doc.modified), "modified_by": doc.modified_by,
			"owner": doc.owner,
		},
		"domains": domains,
		"history": history,
		"can_edit": can_edit,
		"domain_options": list(DOMAINS),
		"max_score": MAX_SCORE,
		"summary": {
			"average_current": round(sum(d["current_score"] for d in assessed) / count, 2),
			"average_target": round(sum(d["target_score"] for d in assessed) / count, 2),
			"total_gap": sum(d["gap"] for d in domains),
			"assessed_domains": len(assessed),
			"priority_areas": [{"domain": d["domain"], "gap": d["gap"],
			                    "priority": d["priority"]} for d in priority_areas],
		},
	}


@frappe.whitelist(methods=["POST"])
def save_henderson_analysis(company: str | None = None, assessment_date: str | None = None,
                            domains=None, summary_notes: str | None = None,
                            status: str | None = None, name: str | None = None):
	"""Create or update an assessment. Management/administrator roles only."""
	_require_write()
	company = (company or "").strip() or frappe.defaults.get_user_default("Company") \
		or frappe.db.get_default("company")
	if not company or not frappe.db.exists("Company", company):
		frappe.throw(_("A valid Company is required."), frappe.ValidationError)

	rows = json.loads(domains) if isinstance(domains, str) else (domains or [])
	if not isinstance(rows, list):
		frappe.throw(_("Invalid domain data."), frappe.ValidationError)

	if name:
		if not frappe.has_permission(DOCTYPE, "write", doc=name):
			frappe.throw(_("You cannot edit this assessment."), frappe.PermissionError)
		doc = frappe.get_doc(DOCTYPE, name)
	else:
		doc = frappe.new_doc(DOCTYPE)
		doc.company = company

	doc.assessment_date = assessment_date or nowdate()
	if status:
		doc.status = status
	doc.summary_notes = summary_notes or ""

	doc.set("domains", [])
	for row in rows:
		domain = str((row or {}).get("domain") or "").strip()
		if domain not in DOMAINS:
			frappe.throw(
				_("{0} is not a Henderson domain. Allowed: {1}.").format(
					domain or "(blank)", ", ".join(DOMAINS)),
				frappe.ValidationError,
			)
		doc.append("domains", {
			"domain": domain,
			"current_score": cint((row or {}).get("current_score")),
			"target_score": cint((row or {}).get("target_score")),
			"priority": (row or {}).get("priority") or "Medium",
			"notes": (row or {}).get("notes") or "",
		})

	doc.save()
	return {"name": doc.name, "modified": str(doc.modified), "modified_by": doc.modified_by}
