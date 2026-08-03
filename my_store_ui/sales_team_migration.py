"""Guarded backfill of the sales team snapshot onto existing data.

    bench --site staging.local execute my_store_ui.sales_team_migration.inspect
    bench --site staging.local execute my_store_ui.sales_team_migration.dry_run
    bench --site staging.local execute my_store_ui.sales_team_migration.apply_safe
    bench --site staging.local execute my_store_ui.sales_team_migration.verify
    bench --site staging.local execute my_store_ui.sales_team_migration.export_manual_review

What it will do: fill the snapshot on **draft** Sales Orders whose customer has an
unambiguous, active, in-company team.

What it will never do: invent a team for a customer that has none, guess the team a
submitted historical document was raised with, rewrite a submitted document, or
touch an accounting, stock or total figure. Documents it cannot settle honestly are
exported for a human to decide on.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timedelta

import frappe
from frappe.utils import cint, flt

# Sites this tool must never write to. site1.local holds real seeded business data.
PROTECTED_SITES = ("site1.local",)
# Only sites explicitly known to be disposable may be written to.
WRITABLE_SITES = ("staging.local",)

SNAPSHOT_DOCTYPES = ("Sales Order", "Delivery Note", "Sales Invoice")
BACKUP_MAX_AGE_HOURS = 24
BATCH_SIZE = 100
MAX_BATCHES = 200


class MigrationRefused(Exception):
	"""Raised instead of writing when a guardrail is not satisfied."""


# --------------------------------------------------------------------------
# Guardrails
# --------------------------------------------------------------------------

def _site() -> str:
	return frappe.local.site


def _assert_readable() -> None:
	if not frappe.db.exists("DocType", "Retail Sales Team"):
		raise MigrationRefused("Retail Sales Team is not installed on this site.")


def _assert_writable() -> None:
	"""Refuse anything but a site explicitly known to be safe to write."""
	site = _site()
	if site in PROTECTED_SITES:
		raise MigrationRefused(
			f"{site} is protected and holds real business data. Refusing to write.")
	if site not in WRITABLE_SITES:
		raise MigrationRefused(
			f"{site} is not a known disposable site. Add it to WRITABLE_SITES only if "
			f"losing its data is acceptable. Refusing to write.")
	_assert_recent_backup()


def _assert_recent_backup() -> None:
	"""A write mode requires a backup taken in the last day."""
	directory = frappe.get_site_path("private", "backups")
	if not os.path.isdir(directory):
		raise MigrationRefused(f"No backup directory at {directory}. Take a backup first.")
	newest = None
	for entry in os.listdir(directory):
		if not entry.endswith("-database.sql.gz"):
			continue
		taken = datetime.fromtimestamp(os.path.getmtime(os.path.join(directory, entry)))
		if newest is None or taken > newest:
			newest = taken
	if newest is None:
		raise MigrationRefused("No database backup found. Run `bench backup --with-files` first.")
	age = datetime.now() - newest
	if age > timedelta(hours=BACKUP_MAX_AGE_HOURS):
		raise MigrationRefused(
			f"The newest backup is {age.days}d {age.seconds // 3600}h old. "
			f"Take a fresh backup before writing.")


# --------------------------------------------------------------------------
# Inspection
# --------------------------------------------------------------------------

def _customer_position() -> dict:
	total = frappe.db.count("Customer")
	assigned = frappe.get_all(
		"Customer", filters={"custom_sales_team": ["is", "set"]},
		fields=["name", "custom_sales_team"], limit_page_length=0)
	teams = {row["custom_sales_team"] for row in assigned}
	active = set(frappe.get_all(
		"Retail Sales Team", filters={"name": ["in", list(teams)] or [""], "is_active": 1},
		pluck="name")) if teams else set()
	existing = set(frappe.get_all(
		"Retail Sales Team", filters={"name": ["in", list(teams)] or [""]},
		pluck="name")) if teams else set()

	return {
		"customers": total,
		"with_team": len(assigned),
		"without_team": total - len(assigned),
		"invalid_team": sorted(
			row["name"] for row in assigned if row["custom_sales_team"] not in existing),
		"inactive_team": sorted(
			row["name"] for row in assigned
			if row["custom_sales_team"] in existing and row["custom_sales_team"] not in active),
	}


def _document_position() -> dict:
	position = {}
	for doctype in SNAPSHOT_DOCTYPES:
		meta = frappe.get_meta(doctype, cached=False)
		if not meta.get_field("custom_sales_team_snapshot"):
			position[doctype] = {"field_installed": False}
			continue
		position[doctype] = {
			"field_installed": True,
			"total": frappe.db.count(doctype),
			"draft": frappe.db.count(doctype, {"docstatus": 0}),
			"submitted": frappe.db.count(doctype, {"docstatus": 1}),
			"cancelled": frappe.db.count(doctype, {"docstatus": 2}),
			"with_snapshot": frappe.db.count(doctype, {"custom_sales_team": ["is", "set"]}),
			"draft_without_snapshot": frappe.db.count(
				doctype, {"docstatus": 0, "custom_sales_team": ["is", "not set"]}),
			"submitted_without_snapshot": frappe.db.count(
				doctype, {"docstatus": 1, "custom_sales_team": ["is", "not set"]}),
		}
	return position


def _team_position() -> dict:
	teams = frappe.get_all(
		"Retail Sales Team", fields=["name", "team_name", "is_active", "commission_rate"],
		limit_page_length=0)
	problems = []
	for team in teams:
		members = frappe.get_all(
			"Retail Sales Team Member",
			filters={"parent": team["name"], "parenttype": "Retail Sales Team", "is_active": 1},
			fields=["sales_person", "team_role", "share_percentage"], limit_page_length=0)
		total = round(sum(flt(m["share_percentage"]) for m in members), 4)
		people = [m["sales_person"] for m in members]
		managers = [m for m in members if m["team_role"] == "Sales Manager"]
		if abs(total - 100.0) > 0.01:
			problems.append({"team": team["name"], "problem": "shares do not total 100",
			                 "detail": total})
		if len(people) != len(set(people)):
			problems.append({"team": team["name"], "problem": "duplicate member"})
		if len(managers) != 1:
			problems.append({"team": team["name"], "problem": "not exactly one active manager",
			                 "detail": len(managers)})
		if not flt(team["commission_rate"]):
			problems.append({"team": team["name"],
			                 "problem": "commission rate is 0; amounts pending configuration"})
	return {
		"teams": len(teams),
		"active": len([t for t in teams if t["is_active"]]),
		"problems": problems,
	}


def _candidates() -> tuple[list[dict], list[dict]]:
	"""Draft orders we can settle honestly, and everything needing a human.

	A draft order is only settled when its customer has exactly one team, that team
	exists, is active, and is not pinned to a different company.
	"""
	settle, review = [], []
	if not frappe.get_meta("Sales Order", cached=False).get_field("custom_sales_team_snapshot"):
		return settle, review

	drafts = frappe.get_all(
		"Sales Order", filters={"docstatus": 0, "custom_sales_team": ["is", "not set"]},
		fields=["name", "customer", "company"], limit_page_length=0)
	for order in drafts:
		team = frappe.db.get_value("Customer", order["customer"], "custom_sales_team")
		if not team:
			review.append({**order, "doctype": "Sales Order",
			               "reason": "customer has no sales team"})
			continue
		row = frappe.db.get_value(
			"Retail Sales Team", team, ["name", "is_active", "restrict_to_company"], as_dict=True)
		if not row:
			review.append({**order, "doctype": "Sales Order", "team": team,
			               "reason": "customer's team no longer exists"})
			continue
		if not row["is_active"]:
			review.append({**order, "doctype": "Sales Order", "team": team,
			               "reason": "customer's team is inactive"})
			continue
		if row["restrict_to_company"] and row["restrict_to_company"] != order["company"]:
			review.append({**order, "doctype": "Sales Order", "team": team,
			               "reason": "team belongs to another company"})
			continue
		settle.append({**order, "team": team})

	# Submitted documents are never guessed at. They are listed so a human can decide.
	for doctype in SNAPSHOT_DOCTYPES:
		if not frappe.get_meta(doctype, cached=False).get_field("custom_sales_team_snapshot"):
			continue
		for row in frappe.get_all(
			doctype, filters={"docstatus": 1, "custom_sales_team": ["is", "not set"]},
			fields=["name", "customer", "company"], limit_page_length=0,
		):
			review.append({
				**row, "doctype": doctype,
				"reason": "submitted before the feature existed; no historical team evidence",
			})
	return settle, review


def _report(mode: str, extra: dict | None = None) -> dict:
	report = {
		"mode": mode,
		"site": _site(),
		"customers": _customer_position(),
		"documents": _document_position(),
		"teams": _team_position(),
	}
	report.update(extra or {})
	return report


def _emit(report: dict) -> dict:
	print(json.dumps(report, indent=1, default=str))
	return report


# --------------------------------------------------------------------------
# Modes
# --------------------------------------------------------------------------

def inspect() -> dict:
	"""Read-only. What exists today."""
	_assert_readable()
	settle, review = _candidates()
	return _emit(_report("inspect", {
		"settleable_draft_orders": len(settle),
		"needing_manual_review": len(review),
	}))


def dry_run() -> dict:
	"""Read-only. Exactly what apply_safe would change, and nothing else."""
	_assert_readable()
	settle, review = _candidates()
	return _emit(_report("dry_run", {
		"would_update": [{"doctype": "Sales Order", "name": row["name"], "team": row["team"]}
		                 for row in settle],
		"would_update_count": len(settle),
		"would_skip_count": len(review),
		"would_touch_submitted_documents": False,
		"would_change_accounting_or_stock": False,
	}))


def apply_safe(commit: bool = True) -> dict:
	"""Write. Draft Sales Orders only, and only where the team is unambiguous.

	`commit=False` leaves the transaction open, so a caller that wrapped this in its
	own savepoint (the test suite) can still roll the whole thing back.
	"""
	# The site guard runs first, so a protected site is refused for being protected
	# rather than incidentally, because the app happens not to be installed there.
	_assert_writable()
	_assert_readable()
	frappe.set_user("Administrator")

	settle, review = _candidates()
	updated, failed = [], []
	batches = 0
	for start in range(0, len(settle), BATCH_SIZE):
		if batches >= MAX_BATCHES:
			break
		batches += 1
		for row in settle[start:start + BATCH_SIZE]:
			# One savepoint per document: a bad record is skipped without discarding
			# the ones already settled, and without touching an outer transaction.
			point = f"stm_backfill_{frappe.generate_hash(length=8)}"
			frappe.db.savepoint(point)
			try:
				doc = frappe.get_doc("Sales Order", row["name"])
				if doc.docstatus != 0:
					continue                      # changed under us; leave it alone
				if doc.get("custom_sales_team"):
					continue                      # already settled; idempotent
				# save() runs freeze_team in before_validate, so the snapshot is built
				# by exactly the same code a new order uses. No parallel write path.
				doc.save()
				updated.append({"name": doc.name, "team": doc.custom_sales_team})
			except Exception as caught:
				frappe.db.rollback(save_point=point)
				failed.append({"name": row["name"], "error": str(caught)})
	if commit:
		frappe.db.commit()

	return _emit(_report("apply_safe", {
		"updated": updated,
		"updated_count": len(updated),
		"failed": failed,
		"skipped_for_manual_review": len(review),
		"submitted_documents_touched": 0,
	}))


def verify() -> dict:
	"""Read-only. Did apply_safe leave the data consistent?"""
	_assert_readable()
	settle, review = _candidates()
	mismatched = []
	for row in frappe.get_all(
		"Sales Order", filters={"custom_sales_team": ["is", "set"]},
		fields=["name", "custom_sales_team", "custom_sales_team_source",
		        "custom_customer_sales_team", "docstatus"], limit_page_length=0,
	):
		rows = frappe.get_all(
			"Retail Sales Team Snapshot",
			filters={"parent": row["name"], "parenttype": "Sales Order",
			         "parentfield": "custom_sales_team_members"},
			fields=["allocation_percentage"], limit_page_length=0)
		if not rows:
			mismatched.append({"name": row["name"], "problem": "team set but no snapshot rows"})
			continue
		total = round(sum(flt(r["allocation_percentage"]) for r in rows), 4)
		if abs(total - 100.0) > 0.01:
			mismatched.append({"name": row["name"], "problem": "allocation does not total 100",
			                   "detail": total})
	return _emit(_report("verify", {
		"remaining_settleable_drafts": len(settle),
		"still_needing_manual_review": len(review),
		"inconsistent_documents": mismatched,
		"consistent": not mismatched and not settle,
	}))


def export_manual_review() -> dict:
	"""Read-only. Write the human-decision list to a CSV outside the repository."""
	_assert_readable()
	_settle, review = _candidates()
	position = _customer_position()

	rows = [
		{"kind": "document", "doctype": r["doctype"], "name": r["name"],
		 "customer": r.get("customer", ""), "company": r.get("company", ""),
		 "team": r.get("team", ""), "reason": r["reason"]}
		for r in review
	]
	rows += [
		{"kind": "customer", "doctype": "Customer", "name": name, "customer": name,
		 "company": "", "team": "", "reason": "no sales team assigned"}
		for name in frappe.get_all(
			"Customer", filters={"custom_sales_team": ["is", "not set"]},
			pluck="name", limit_page_length=0)
	]
	rows += [
		{"kind": "customer", "doctype": "Customer", "name": name, "customer": name,
		 "company": "", "team": "", "reason": "assigned team is inactive"}
		for name in position["inactive_team"]
	]
	rows += [
		{"kind": "customer", "doctype": "Customer", "name": name, "customer": name,
		 "company": "", "team": "", "reason": "assigned team no longer exists"}
		for name in position["invalid_team"]
	]
	for problem in _team_position()["problems"]:
		rows.append({"kind": "team", "doctype": "Retail Sales Team",
		             "name": problem["team"], "customer": "", "company": "", "team": problem["team"],
		             "reason": f"{problem['problem']} ({problem.get('detail', '')})".strip()})

	# Site private files, never the repository.
	path = frappe.get_site_path("private", "files", "sales_team_manual_review.csv")
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", newline="") as handle:
		writer = csv.DictWriter(
			handle, fieldnames=["kind", "doctype", "name", "customer", "company", "team", "reason"])
		writer.writeheader()
		writer.writerows(rows)

	return _emit(_report("export_manual_review", {"path": path, "rows": len(rows)}))


def run(mode: str = "inspect") -> dict:
	modes = {"inspect": inspect, "dry_run": dry_run, "apply_safe": apply_safe,
	         "verify": verify, "export_manual_review": export_manual_review}
	if mode not in modes:
		raise MigrationRefused(f"Unknown mode {mode!r}. One of: {', '.join(modes)}")
	return modes[mode]()
