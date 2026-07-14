"""Reproducible server-side verification of generated clean routes.

Runs the exact resolution + universal-engine path the Vue clean routes use, as
the current user, so a route is only credited when it genuinely resolves and the
permission-checked list API returns. Run:

    bench --site site1.local execute my_store_ui.audit.route_coverage.verify_generated_routes

This is verification, not a mutation: it performs only reads.
"""
from __future__ import annotations

import frappe

from my_store_ui import priority_pages
from my_store_ui.services.priority_registry import ENTITY_ROUTES
from my_store_ui.universal import api as universal_api


def verify_generated_routes(limit_per_route: int = 2) -> dict:
    """Resolve every ENTITY_ROUTES base and exercise the universal list path.

    Returns pass/fail detail. A PermissionError is reported separately (it means
    the current user lacks access, not that the route is broken).
    """
    served, permission_denied, failures = [], [], []
    for path, spec in sorted(ENTITY_ROUTES.items()):
        doctype = spec.get("doctype")
        if not doctype:
            continue
        try:
            definition = priority_pages.get_priority_route_definition(path)
            feature = definition.get("feature")
            if not feature:
                failures.append({"path": path, "doctype": doctype, "error": "no feature key"})
                continue
            universal_api.get_list_configuration(feature)
            universal_api.get_document_list(feature, page=1, page_size=limit_per_route)
            served.append(doctype)
        except frappe.PermissionError:
            permission_denied.append({"path": path, "doctype": doctype})
        except Exception as exc:  # noqa: BLE001 - report, do not raise
            failures.append({"path": path, "doctype": doctype, "error": f"{type(exc).__name__}: {exc}"})
    return {
        "status": "pass" if not failures else "fail",
        "served": len(served),
        "permission_denied": len(permission_denied),
        "failed": len(failures),
        "failures": failures[:50],
    }
