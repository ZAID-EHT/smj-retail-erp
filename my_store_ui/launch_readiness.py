"""Phase 6 — truthful go-live readiness dashboard (read-only, manager-gated).

Reports the real state of each launch item. Never marks an external requirement
"complete" merely because a document or script exists — items that depend on
accountant approval, credentials, deployment or UAT stay "pending external action"
or "awaiting approval". Exposes no server credentials or private paths.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint

from my_store_ui.access_management import _email_configuration_status, _require_user_manager

# Allowed statuses (the UI renders these).
VERIFIED = "Verified"
COMPLETE = "Complete"
PENDING_EXTERNAL = "Pending external action"
AWAITING_APPROVAL = "Awaiting approval"
CREDENTIAL_REQUIRED = "Credential required"
NOT_STARTED = "Not started"
FAILED = "Failed"
NOT_APPLICABLE = "Not applicable"


def _item(category, name, status, owner=None, action=None, route=None, doc=None, risk=None):
	return {"category": category, "name": name, "status": status, "owner": owner,
	        "action": action, "route": route, "doc": doc, "risk": risk,
	        "blocker": status in (PENDING_EXTERNAL, AWAITING_APPROVAL, CREDENTIAL_REQUIRED, FAILED, NOT_STARTED)}


def _finance_items() -> list[dict]:
	company = (frappe.get_all("Company", pluck="name", limit_page_length=1) or [None])[0]
	applied = frappe.db.get_value(
		"Journal Entry", {"user_remark": ["like", "%opening-stock reclassification%"], "docstatus": 1}, "name") if company else None
	pending = False
	if company:
		sa = frappe.db.get_value("Company", company, "stock_adjustment_account")
		if sa:
			pending = bool(frappe.db.sql(
				"""SELECT 1 FROM `tabGL Entry` WHERE account=%s AND is_cancelled=0
				   AND voucher_type='Stock Entry' AND posting_date<=%s LIMIT 1""", (sa, "2025-07-01")))
	c = "Finance"
	return [
		_item(c, "Opening-stock issue identified", VERIFIED, doc="docs/finance/SMJ_OPENING_STOCK_CONFIRMED_ROOT_CAUSE.md"),
		_item(c, "Root cause confirmed", VERIFIED, doc="docs/finance/SMJ_OPENING_STOCK_CONFIRMED_ROOT_CAUSE.md"),
		_item(c, "Correction package prepared", VERIFIED, doc="docs/finance/SMJ_ACCOUNTANT_CORRECTION_PACKAGE.md"),
		_item(c, "Dry-run verified", VERIFIED, doc="docs/finance/SMJ_FINANCE_QA_EXECUTION_RESULT.md"),
		_item(c, "Accountant approval", AWAITING_APPROVAL, owner="Accountant",
		      action="Review and approve the reclassification", doc="docs/release/SMJ_ACCOUNTANT_SIGNOFF_CHECKLIST.md",
		      risk="P&L overstated until applied"),
		_item(c, "Correction Journal Entry submitted", AWAITING_APPROVAL if pending and not applied else (COMPLETE if applied else NOT_APPLICABLE),
		      owner="Accountant", action="Apply after sign-off", route="/admin/readiness"),
		_item(c, "Financial reports reconciled after correction", NOT_STARTED if pending and not applied else (VERIFIED if applied else NOT_APPLICABLE),
		      owner="Accountant"),
	]


def _code_items() -> list[dict]:
	from my_store_ui.system_operations import _has_pending_migration
	c = "Code & release"
	return [
		_item(c, "Backend test suite", VERIFIED, doc="docs/verification/SMJ_FINAL_ACCEPTANCE_MATRIX.md"),
		_item(c, "Frontend build", VERIFIED),
		_item(c, "Browser matrix (6 viewports)", VERIFIED, doc="docs/verification/SMJ_RC4_BROWSER_MATRIX.md"),
		_item(c, "Secret scan", VERIFIED, doc="docs/release/SMJ_RELEASE_REHEARSAL_RESULT.md"),
		_item(c, "Pending migrations", COMPLETE if not _has_pending_migration() else FAILED),
	]


def _setup_items() -> list[dict]:
	c = "Setup"
	company_count = frappe.db.count("Company")
	return [
		_item(c, "First-time setup wizard", VERIFIED, route="/setup"),
		_item(c, "Company creation", VERIFIED if company_count else NOT_STARTED, route="/admin/companies"),
		_item(c, "Two-company separation", VERIFIED, doc="docs/security/SMJ_TWO_COMPANY_END_TO_END_SEPARATION.md"),
		_item(c, "Genuine fresh-site test", CREDENTIAL_REQUIRED, owner="Ops",
		      action="Run scripts/verify_fresh_install.sh with MariaDB root", doc="docs/setup/SMJ_GENUINE_FRESH_INSTALL_RESULT.md",
		      risk="Fresh-install path unproven on a physically empty site"),
		_item(c, "Printing & PDF", VERIFIED, route="/admin/printing"),
		_item(c, "Data import/export", VERIFIED, route="/admin/data"),
	]


def _infra_items() -> list[dict]:
	from my_store_ui.system_operations import _scheduler_disabled
	c = "Infrastructure"
	email_ok = _email_configuration_status()["can_send_welcome_email"]
	return [
		_item(c, "SMTP configured", COMPLETE if email_ok else CREDENTIAL_REQUIRED, owner="Ops",
		      action="Create an outgoing Email Account", doc="docs/email/SMJ_SMTP_PRODUCTION_CHECKLIST.md",
		      route="/admin/email", risk="Welcome/reset emails and scheduled reports cannot send"),
		_item(c, "Scheduler enabled", COMPLETE if not _scheduler_disabled() else PENDING_EXTERNAL, owner="Ops",
		      action="bench enable-scheduler", route="/admin/system"),
		_item(c, "Hetzner server + image", CREDENTIAL_REQUIRED, owner="Ops",
		      action="Provision + build/push image", doc="docs/deployment/SMJ_HETZNER_REHEARSAL_PLAN.md"),
		_item(c, "DNS configured", CREDENTIAL_REQUIRED, owner="Ops", doc="deployment/docs/DNS_AND_TLS.md"),
		_item(c, "HTTPS configured", CREDENTIAL_REQUIRED, owner="Ops", doc="deployment/docs/DNS_AND_TLS.md"),
		_item(c, "Backup destination + off-server copy", CREDENTIAL_REQUIRED, owner="Ops", doc="deployment/docs/BACKUP_STRATEGY.md"),
		_item(c, "Restore drill", NOT_STARTED, owner="Ops", doc="deployment/scripts/restore-test.sh"),
		_item(c, "Monitoring", NOT_STARTED, owner="Ops"),
	]


def _approval_items() -> list[dict]:
	c = "Business approval"
	return [
		_item(c, "Accountant approval", AWAITING_APPROVAL, owner="Accountant", doc="docs/release/SMJ_ACCOUNTANT_SIGNOFF_CHECKLIST.md"),
		_item(c, "Client UAT", NOT_STARTED, owner="Client", doc="docs/release/SMJ_CLIENT_UAT_CHECKLIST.md"),
		_item(c, "Management approval", NOT_STARTED, owner="Management"),
		_item(c, "Production cutover approval", NOT_STARTED, owner="Management", doc="docs/deployment/SMJ_PRODUCTION_CUTOVER_PLAN.md"),
	]


@frappe.whitelist(methods=["GET"])
def get_launch_readiness() -> dict:
	_require_user_manager()
	items = _code_items() + _finance_items() + _setup_items() + _infra_items() + _approval_items()
	blockers = [i for i in items if i["blocker"]]
	by_category: dict = {}
	for i in items:
		by_category.setdefault(i["category"], []).append(i)
	return {
		"items": items,
		"by_category": by_category,
		"total": len(items),
		"blocker_count": len(blockers),
		"verified_count": sum(1 for i in items if i["status"] in (VERIFIED, COMPLETE)),
		"summary": _("{0} of {1} items verified/complete; {2} awaiting external action or approval.").format(
			sum(1 for i in items if i["status"] in (VERIFIED, COMPLETE)), len(items), len(blockers)),
	}
