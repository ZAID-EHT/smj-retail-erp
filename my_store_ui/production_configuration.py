"""Is this site actually configured to be production, and what is honest about it.

Every check here is a named function with one job. There is deliberately no
"run this command" endpoint: a configuration checker that accepts a command from
the browser is a remote shell with a reassuring name. The checks read settings,
count rows and ask services whether they are alive; nothing more.

Statuses are chosen so that the page cannot flatter itself:

    Pass            verified here, now
    Warning         works, but not how production should look
    Fail            wrong, and go-live should not proceed
    External        depends on somebody outside this system -- never Pass
    Not Applicable  genuinely does not apply

`External` exists because the alternative is worse. Without it, "DNS configured"
has to be either Pass (a lie) or Fail (implies we broke it); with it, the page
says the true thing, which is that nobody here can answer.
"""

from __future__ import annotations

import os

import frappe
from frappe import _
from frappe.utils import cint, getdate, nowdate

from my_store_ui.access_management import _require_user_manager

PASS = "Pass"
WARNING = "Warning"
FAIL = "Fail"
EXTERNAL = "External"
NOT_APPLICABLE = "Not Applicable"

BACKUP_WARN_HOURS = 24


def _check(group, name, status, detail="", owner=None, action=None):
	return {"group": group, "name": name, "status": status, "detail": detail,
	        "owner": owner, "action": action,
	        "blocking": status == FAIL}


# --------------------------------------------------------------------------
# Application
# --------------------------------------------------------------------------

def _application_checks() -> list[dict]:
	group = "Application"
	out = []

	developer_mode = cint(frappe.conf.get("developer_mode") or 0)
	out.append(_check(
		group, "Developer mode disabled",
		PASS if not developer_mode else FAIL,
		"developer_mode is off" if not developer_mode
		else "developer_mode is on; DocType changes would be written to disk",
		owner="Ops", action="Remove developer_mode from site config"))

	allow_tests = cint(frappe.conf.get("allow_tests") or 0)
	out.append(_check(
		group, "Test mode disabled",
		PASS if not allow_tests else FAIL,
		"allow_tests is off" if not allow_tests
		else "allow_tests is on; test fixtures could be created against real data",
		owner="Ops", action="Remove allow_tests from site config"))

	from my_store_ui.system_operations import _has_pending_migration
	pending = _has_pending_migration()
	out.append(_check(
		group, "Migrations complete", PASS if not pending else FAIL,
		"no pending patches" if not pending else "patches are pending",
		owner="Ops", action="bench --site <site> migrate"))

	assets = os.path.isdir(frappe.get_app_path("my_store_ui", "public", "frontend",
	                                           "assets"))
	out.append(_check(
		group, "Frontend assets built", PASS if assets else FAIL,
		"built assets present" if assets else "no built frontend assets found",
		owner="Ops", action="npm run build"))

	installed = set(frappe.get_installed_apps())
	required = {"frappe", "erpnext", "my_store_ui"}
	missing = sorted(required - installed)
	out.append(_check(
		group, "Required apps installed", PASS if not missing else FAIL,
		"frappe, erpnext, my_store_ui present" if not missing
		else f"missing: {', '.join(missing)}"))

	return out


# --------------------------------------------------------------------------
# Services
# --------------------------------------------------------------------------

def _service_checks() -> list[dict]:
	from my_store_ui.system_operations import _redis_ok, _scheduler_disabled

	group = "Services"
	out = []

	try:
		frappe.db.sql("select 1")
		db_ok = True
	except Exception:
		db_ok = False
	out.append(_check(group, "Database reachable", PASS if db_ok else FAIL,
	                  "MariaDB responded" if db_ok else "MariaDB did not respond"))

	for key, label in (("redis_cache", "Redis cache"), ("redis_queue", "Redis queue")):
		ok = _redis_ok(key)
		out.append(_check(group, f"{label} reachable", PASS if ok else FAIL,
		                  "responded" if ok else "did not respond",
		                  owner="Ops"))

	disabled = _scheduler_disabled()
	out.append(_check(
		group, "Scheduler enabled", PASS if not disabled else FAIL,
		"scheduler is enabled" if not disabled else "scheduler is disabled; "
		"scheduled reports and background jobs will not run",
		owner="Ops", action="bench --site <site> enable-scheduler"))

	# Whether a worker is consuming the queue cannot be proven from inside a web
	# request without enqueuing something, so this reports what it can and says so.
	out.append(_check(
		group, "Background workers", EXTERNAL,
		"worker health is observed from the process manager, not from here",
		owner="Ops", action="Confirm workers are running on the host"))

	return out


# --------------------------------------------------------------------------
# Business setup
# --------------------------------------------------------------------------

def _business_checks() -> list[dict]:
	group = "Business setup"
	out = []

	companies = frappe.get_all("Company", pluck="name")
	out.append(_check(group, "Company created", PASS if companies else FAIL,
	                  f"{len(companies)} company(ies)" if companies
	                  else "no company exists"))

	today = getdate(nowdate())
	fiscal = frappe.get_all(
		"Fiscal Year", filters={"year_start_date": ["<=", today],
		                        "year_end_date": [">=", today], "disabled": 0},
		pluck="name")
	out.append(_check(group, "Active fiscal year", PASS if fiscal else FAIL,
	                  f"{fiscal[0]}" if fiscal else "no fiscal year covers today"))

	accounts = frappe.db.count("Account")
	out.append(_check(group, "Chart of accounts", PASS if accounts > 10 else FAIL,
	                  f"{accounts} accounts"))

	cost_centers = frappe.db.count("Cost Center", {"is_group": 0})
	out.append(_check(group, "Cost centre", PASS if cost_centers else WARNING,
	                  f"{cost_centers} cost centre(s)"))

	warehouses = frappe.db.count("Warehouse", {"is_group": 0, "disabled": 0})
	out.append(_check(group, "Warehouses", PASS if warehouses else FAIL,
	                  f"{warehouses} active warehouse(s)"))

	selling = frappe.db.count("Price List", {"selling": 1, "enabled": 1})
	buying = frappe.db.count("Price List", {"buying": 1, "enabled": 1})
	out.append(_check(group, "Selling price lists", PASS if selling else FAIL,
	                  f"{selling} enabled selling price list(s)"))
	out.append(_check(group, "Buying price list", PASS if buying else FAIL,
	                  f"{buying} enabled buying price list(s)"))

	users = frappe.db.count("User", {"enabled": 1})
	out.append(_check(group, "User accounts", PASS if users > 1 else WARNING,
	                  f"{users} enabled user(s)"))

	return out


# --------------------------------------------------------------------------
# Security
# --------------------------------------------------------------------------

TEST_USER_PATTERNS = ("%@example.com", "%test%")


def _security_checks() -> list[dict]:
	group = "Security"
	out = []

	host = frappe.conf.get("host_name") or ""
	if not host:
		status, detail = EXTERNAL, "no host_name configured; HTTPS is set on the host"
	elif host.startswith("https://"):
		status, detail = PASS, "host_name uses https"
	else:
		status, detail = FAIL, f"host_name is not https"
	out.append(_check(group, "HTTPS hostname", status, detail, owner="Ops"))

	test_users = []
	for pattern in TEST_USER_PATTERNS:
		test_users += frappe.get_all(
			"User", filters={"email": ["like", pattern], "enabled": 1}, pluck="name")
	test_users = sorted(set(test_users) - {"Administrator", "Guest"})
	out.append(_check(
		group, "No enabled test users", PASS if not test_users else FAIL,
		"none found" if not test_users
		else f"{len(test_users)} enabled test-pattern user(s)",
		owner="Ops", action="Disable or delete test accounts"))

	test_warehouses = frappe.get_all(
		"Warehouse", filters={"warehouse_name": ["like", "%test%"], "disabled": 0},
		pluck="name")
	out.append(_check(
		group, "No enabled test warehouses",
		PASS if not test_warehouses else WARNING,
		"none found" if not test_warehouses
		else f"{len(test_warehouses)} test-named warehouse(s)"))

	# Never report what the secret is -- only whether one is configured.
	out.append(_check(
		group, "Encryption key configured",
		PASS if frappe.conf.get("encryption_key") else WARNING,
		"configured" if frappe.conf.get("encryption_key") else "not configured"))

	return out


# --------------------------------------------------------------------------
# Operations
# --------------------------------------------------------------------------

def _operations_checks() -> list[dict]:
	group = "Operations"
	out = []

	from my_store_ui.finance.accounting_preparation import _latest_backup_age_hours
	age = _latest_backup_age_hours()
	if age is None:
		out.append(_check(group, "Recent backup", FAIL, "no backup found",
		                  owner="Ops", action="bench --site <site> backup --with-files"))
	elif age > BACKUP_WARN_HOURS:
		out.append(_check(group, "Recent backup", WARNING,
		                  f"newest backup is {age:.1f} hours old", owner="Ops"))
	else:
		out.append(_check(group, "Recent backup", PASS,
		                  f"newest backup is {age:.1f} hours old"))

	out.append(_check(
		group, "Off-server backup destination", EXTERNAL,
		"a backup that lives only on the server it backs up is not a backup",
		owner="Ops", action="Configure and verify a remote destination"))
	out.append(_check(
		group, "Restore drill", EXTERNAL,
		"restoring into a scratch site on real infrastructure is an owner action",
		owner="Ops"))
	out.append(_check(
		group, "Monitoring", EXTERNAL,
		"monitoring and alerting are configured outside this system", owner="Ops"))

	errors = frappe.db.count("Error Log", {"creation": [">", frappe.utils.add_days(nowdate(), -1)]})
	out.append(_check(
		group, "Error trend (24h)",
		PASS if errors < 25 else WARNING, f"{errors} error log entries in 24 hours"))

	return out


# --------------------------------------------------------------------------
# Finance and approvals
# --------------------------------------------------------------------------

def _finance_checks() -> list[dict]:
	from my_store_ui.finance import accountant_decisions as decisions
	from my_store_ui.finance import opening_stock_correction as osc

	group = "Finance and approvals"
	out = []
	company = (frappe.get_all("Company", pluck="name", limit_page_length=1) or [None])[0]

	if company:
		unresolved_stock = decisions.unresolved_topics(
			decisions.AREA_OPENING_STOCK, company)
		unresolved_comm = decisions.unresolved_topics(
			decisions.AREA_COMMISSION, company)
	else:
		unresolved_stock = unresolved_comm = []

	out.append(_check(
		group, "Opening-stock accountant decisions",
		PASS if company and not unresolved_stock else EXTERNAL,
		"all recorded" if company and not unresolved_stock
		else f"{len(unresolved_stock)} decision(s) awaiting an accountant",
		owner="Accountant"))

	try:
		submitted = osc._applied_je(osc._context(), 1)
	except Exception:
		submitted = None
	out.append(_check(
		group, "Opening-stock correction posted",
		PASS if submitted else EXTERNAL,
		f"submitted as {submitted}" if submitted
		else "not submitted; submission is an accountant action",
		owner="Accountant"))

	out.append(_check(
		group, "Commission accountant decisions",
		PASS if company and not unresolved_comm else EXTERNAL,
		"all recorded" if company and not unresolved_comm
		else f"{len(unresolved_comm)} decision(s) awaiting an accountant",
		owner="Accountant"))

	out.append(_check(
		group, "Commission posting", NOT_APPLICABLE,
		"commission posting is disabled in this build and cannot be enabled by "
		"configuration"))

	from my_store_ui.external_actions import go_live_blockers_count
	blocking = go_live_blockers_count()
	out.append(_check(
		group, "External go-live actions",
		PASS if not blocking else EXTERNAL,
		"none outstanding" if not blocking
		else f"{blocking} blocking external action(s) outstanding",
		owner="Ops", action="See the External Actions tracker"))

	return out


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

CHECK_GROUPS = (
	_application_checks, _service_checks, _business_checks,
	_security_checks, _operations_checks, _finance_checks,
)


@frappe.whitelist(methods=["GET"])
def get_production_configuration() -> dict:
	"""Every check, grouped, with a truthful headline."""
	_require_user_manager()
	checks: list[dict] = []
	for group_fn in CHECK_GROUPS:
		try:
			checks.extend(group_fn())
		except Exception as exc:
			# A failing check must report itself, not take the page down.
			checks.append(_check(
				group_fn.__name__.strip("_").replace("_checks", "").title(),
				"Check failed to run", FAIL, str(exc)[:200]))

	by_group: dict = {}
	for check in checks:
		by_group.setdefault(check["group"], []).append(check)

	counts = {status: sum(1 for c in checks if c["status"] == status)
	          for status in (PASS, WARNING, FAIL, EXTERNAL, NOT_APPLICABLE)}
	failing = [c for c in checks if c["status"] == FAIL]

	return {
		"checks": checks,
		"by_group": by_group,
		"counts": counts,
		"total": len(checks),
		"failing": failing,
		"production_ready": not failing and counts[EXTERNAL] == 0,
		"locally_clean": not failing,
		"statuses": [PASS, WARNING, FAIL, EXTERNAL, NOT_APPLICABLE],
		"summary": _(
			"{0} pass, {1} warning, {2} fail, {3} external, {4} not applicable. "
			"External items cannot be resolved from this system."
		).format(counts[PASS], counts[WARNING], counts[FAIL], counts[EXTERNAL],
		         counts[NOT_APPLICABLE]),
	}
