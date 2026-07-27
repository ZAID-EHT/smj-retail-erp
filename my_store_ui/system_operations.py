"""Phase 12 — safe, read-only system operations and readiness.

Every endpoint is System Manager gated and returns only fixed-purpose, allowlisted
status. There is NO arbitrary shell execution, NO database credential exposure, NO
unrestricted path exposure, and NO web-based restore. The one write action
(request a backup) uses Frappe's own supported backup mechanism.
"""

from __future__ import annotations

import os

import frappe
from frappe import _
from frappe.utils import cint, flt, now_datetime, get_datetime

from my_store_ui.access_management import _require_user_manager


def _scheduler_disabled() -> bool:
	"""Scheduler state via the supported helper, with safe fallbacks."""
	try:
		from frappe.utils.scheduler import is_scheduler_disabled
		return bool(is_scheduler_disabled(verbose=False))
	except TypeError:
		from frappe.utils.scheduler import is_scheduler_disabled
		return bool(is_scheduler_disabled())
	except Exception:
		return bool(cint(frappe.conf.get("scheduler_enabled") is False) or cint(frappe.conf.get("pause_scheduler") or 0))


def _redis_ok(key: str) -> bool:
	try:
		conn = getattr(frappe.cache(), "redis", None) or frappe.cache()
		conn.ping() if hasattr(conn, "ping") else conn.get_value("__ping__")
		return True
	except Exception:
		return False


@frappe.whitelist(methods=["GET"])
def get_system_health() -> dict:
	"""Fixed-purpose health status. No credentials, no paths, no shell."""
	_require_user_manager()

	# Database
	try:
		frappe.db.sql("SELECT 1")
		db_ok = True
	except Exception:
		db_ok = False

	# Scheduler -- driven by site config / the scheduler helper, not System Settings.
	scheduler_disabled = _scheduler_disabled()

	# Error Log trend (last 24h vs prior 24h) -- counts only, no content.
	errors_24h = frappe.db.count("Error Log", {"creation": [">", frappe.utils.add_days(now_datetime(), -1)]})
	errors_prev = frappe.db.count("Error Log", {
		"creation": ["between", [frappe.utils.add_days(now_datetime(), -2), frappe.utils.add_days(now_datetime(), -1)]],
	})

	# Background jobs / queue health (counts only).
	failed_jobs = 0
	try:
		failed_jobs = frappe.db.count("RQ Job", {"status": "failed"})
	except Exception:
		failed_jobs = -1  # doctype not available on this version

	return {
		"database": {"connected": db_ok},
		"cache_redis": {"connected": _redis_ok("cache")},
		"scheduler": {"enabled": not scheduler_disabled},  # noqa: E501
		"errors": {"last_24h": errors_24h, "previous_24h": errors_prev,
		           "trend": "up" if errors_24h > errors_prev else ("down" if errors_24h < errors_prev else "flat")},
		"background_jobs": {"failed": failed_jobs},
	}


@frappe.whitelist(methods=["GET"])
def get_readiness() -> dict:
	"""Production-readiness snapshot: config flags and versions, all safe."""
	_require_user_manager()
	from my_store_ui.access_management import _email_configuration_status

	developer_mode = cint(frappe.conf.get("developer_mode") or 0)
	# App versions (name + version only).
	versions = {}
	for app in frappe.get_installed_apps():
		try:
			versions[app] = frappe.get_attr(f"{app}.__version__")
		except Exception:
			versions[app] = None

	companies = frappe.db.count("Company")
	pending_migration = _has_pending_migration()

	return {
		"developer_mode": bool(developer_mode),
		"maintenance_mode": bool(cint(frappe.conf.get("maintenance_mode") or 0)),
		"app_versions": versions,
		"company_count": companies,
		"first_time_setup_required": companies == 0,
		"email_configured": _email_configuration_status()["can_send_welcome_email"],
		"pending_migrations": pending_migration,
		"scheduler_enabled": not _scheduler_disabled(),
	}


def _has_pending_migration() -> bool:
	"""True if any installed app reports unapplied patches. Read-only."""
	try:
		from frappe.modules.patch_handler import get_all_patches
		applied = set(frappe.get_all("Patch Log", pluck="patch"))
		for patch in get_all_patches():
			if patch and patch not in applied:
				return True
	except Exception:
		return False
	return False


@frappe.whitelist(methods=["GET"])
def get_backup_status() -> dict:
	"""Backup history from the site's own backup directory. No paths leaked."""
	_require_user_manager()
	backup_dir = frappe.utils.get_site_path("private", "backups")
	entries = []
	newest = None
	try:
		for fname in os.listdir(backup_dir):
			if not fname.endswith("-database.sql.gz"):
				continue
			full = os.path.join(backup_dir, fname)
			mtime = os.path.getmtime(full)
			size = os.path.getsize(full)
			# Expose only the basename and metadata, never the absolute path.
			entries.append({"file": fname, "size_mb": round(size / (1024 * 1024), 2),
			                "modified": get_datetime(frappe.utils.datetime.datetime.fromtimestamp(mtime))})
			newest = max(newest, mtime) if newest else mtime
	except Exception:
		pass
	entries.sort(key=lambda row: row["modified"], reverse=True)
	age_hours = None
	if newest:
		age_hours = round((now_datetime().timestamp() - newest) / 3600, 1)
	return {
		"backup_count": len(entries),
		"latest_age_hours": age_hours,
		"backups": entries[:10],
		"note": _("Restore is a controlled server-side operation and is not available from the web UI."),
	}


@frappe.whitelist(methods=["GET"])
def get_error_log_summary() -> dict:
	"""Recent Error Log counts by method. No tracebacks, no PII."""
	_require_user_manager()
	if not frappe.has_permission("Error Log", "read"):
		frappe.throw(_("Not permitted."), frappe.PermissionError)
	rows = frappe.db.sql(
		"""SELECT method, COUNT(*) AS count FROM `tabError Log`
		   WHERE creation > %s GROUP BY method ORDER BY count DESC LIMIT 15""",
		frappe.utils.add_days(now_datetime(), -7), as_dict=True,
	)
	return {"since_days": 7, "top_methods": rows,
	        "total_7d": frappe.db.count("Error Log", {"creation": [">", frappe.utils.add_days(now_datetime(), -7)]})}
