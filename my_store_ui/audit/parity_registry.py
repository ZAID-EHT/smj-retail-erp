"""Authoritative Retail ERP parity registry (Stage 2).

This module assigns EVERY user-facing capability discovered by the canonical
feature inventory exactly one truthful status, business priority and
implementation strategy. It is deterministic: it reads the canonical inventory
(`docs/erpnext-v15-complete-inventory.json`) and applies rules + a small,
explicit override table. Nothing here mutates the site.

Honesty contract (enforced by `validate_parity_registry`):
- Every user-facing feature has exactly one registry entry.
- No duplicate feature keys.
- Every entry has a known strategy, status and business priority.
- `verified_complete` requires non-empty evidence.
- A route is never, by itself, treated as completion — mapped-but-unverified
  features are `implemented_unverified` or `generated_provisional`, not
  `verified_complete`.
- `unavailable_with_reason` / `not_required` / `internal` are NOT counted as
  implemented functionality.

Statuses (truthful): verified_complete, implemented_unverified,
generated_provisional, special_adapter, blocked, unavailable_with_reason,
not_required, internal.

Business priorities: P0_go_live, P1_required, P2_important, P3_optional,
not_required, internal.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

STATUSES = {
    "verified_complete", "implemented_unverified", "generated_provisional",
    "special_adapter", "blocked", "unavailable_with_reason", "not_required", "internal",
}
IMPLEMENTED_STATUSES = {"verified_complete", "implemented_unverified", "generated_provisional", "special_adapter"}
PRIORITIES = {"P0_go_live", "P1_required", "P2_important", "P3_optional", "not_required", "internal"}
STRATEGIES = {
    "custom_override", "generated_doctype", "generated_report", "generated_workspace",
    "generated_dashboard", "generated_print", "generated_tree", "generated_calendar",
    "generated_kanban", "generated_query", "special_adapter", "external_app_adapter",
    "unavailable_with_reason", "not_required", "internal",
}

# ---------------------------------------------------------------------------
# Rule tables
# ---------------------------------------------------------------------------

# The six genuinely handcrafted DocTypes (custom_override). Tests are blocked on
# this site, so the strongest honest status is implemented_unverified.
HANDCRAFTED_DOCTYPES = {
    "Customer", "Item", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
}

# P0 documents in the fixed wholesale flow. Priority only — status still comes
# from real implementation state.
P0_DOCTYPES = {
    "Customer", "Item", "Sales Order", "Delivery Note", "Sales Invoice", "Payment Entry",
    "Stock Reservation Entry", "Bin", "Pick List", "Packing Slip", "Customer Credit Limit",
}

# Module -> default business priority for a wholesale IMPORTING & SELLING business.
# Overridden per-feature by type/override rules below.
MODULE_PRIORITY = {
    "Accounts": "P1_required",
    "Stock": "P1_required",
    "Selling": "P1_required",
    "Buying": "P1_required",
    "Contacts": "P1_required",
    "CRM": "P2_important",
    "Setup": "P2_important",
    "POSAwesome": "P2_important",
    "Printing": "P2_important",
    "Regional": "P2_important",
    "Assets": "P3_optional",
    "Projects": "P3_optional",
    "Support": "P3_optional",
    "Quality Management": "P3_optional",
    "Automation": "P3_optional",
    "Workflow": "P3_optional",
    "Bulk Transaction": "P3_optional",
    "Email": "P3_optional",
    "Communication": "P3_optional",
    # Not relevant to the stated wholesale importing/selling scope:
    "Manufacturing": "not_required",
    "Subcontracting": "not_required",
    "Website": "not_required",
    "Portal": "not_required",
    "Social": "not_required",
    "Telephony": "not_required",
    "EDI": "not_required",
    "Maintenance": "not_required",
    "ERPNext Gemini Integration": "not_required",
    "ERPNext ChatGPT": "not_required",
    "Gemini": "not_required",
    "erpnext_chatgpt": "not_required",
    "erpnext_gemini_integration": "not_required",
    # Platform/technical:
    "Core": "internal",
    "Desk": "internal",
    "Custom": "internal",
    "Utilities": "internal",
    "Geo": "internal",
    "Integrations": "P3_optional",
    "ERPNext Integrations": "P3_optional",
}

# Feature types that are components of a parent DocType/workspace rather than
# independent user destinations -> internal by construction.
INTERNAL_FEATURE_TYPES = {
    "custom_field", "property_setter", "client_script", "server_script",
    "workspace_target", "dashboard_connection", "installed_app", "source_only_report",
    "notification",
}

# Feature types that map onto the generic engine when their parent is in scope.
VISUAL_TYPES = {"dashboard", "dashboard_chart", "number_card", "workspace"}


def _canonical_path() -> Path:
    try:
        import frappe  # noqa
        app_path = Path(frappe.get_app_path("my_store_ui")).resolve().parent
    except Exception:
        app_path = Path(__file__).resolve().parents[2]
    return app_path / "docs" / "erpnext-v15-complete-inventory.json"


def _priority_for(feature: dict) -> str:
    name = feature.get("doctype") or feature.get("name")
    if name in P0_DOCTYPES:
        return "P0_go_live"
    return MODULE_PRIORITY.get(feature.get("module") or "", "P3_optional")


def _strategy_and_status(feature: dict, priority: str) -> tuple[str, str, str, list[str], str]:
    """Return (strategy, status, verification_level, evidence, notes)."""
    ftype = feature.get("feature_type")
    doctype = feature.get("doctype")
    route = feature.get("current_custom_route")

    # 0. A workspace shortcut credited with its target's real Retail ERP route is
    # reachable navigation, not an internal component.
    if ftype == "workspace_target" and route:
        return ("generated_doctype", "generated_provisional", "route_only",
                [f"Reachable via mapped destination {route}"],
                "Workspace shortcut resolves to a routed Retail ERP destination; card verification pending.")

    # 1. Any feature carrying a real Retail ERP route is implemented in some form
    # regardless of module/type — evaluate this before internal/priority rules.
    if route:
        if doctype in HANDCRAFTED_DOCTYPES and ftype == "doctype":
            return ("custom_override", "implemented_unverified", "source_only",
                    [f"Handcrafted route {route}", "Server schema + lifecycle actions exist"],
                    "Behavioural verification blocked: allow_tests disabled; no browser automation.")
        if ftype == "report":
            return ("generated_report", "generated_provisional", "route_only",
                    [f"Priority report route {route}"],
                    "Provisional report viewer; interactive filter/chart/PDF tests pending.")
        if ftype == "doctype":
            return ("generated_doctype", "generated_provisional", "route_only",
                    [f"Clean generated route {route}"],
                    "Generic engine route; per-feature action/permission/browser tests pending.")
        # Routed page/shell/installed-app surface (e.g. the /retail-erp SPA shell).
        return ("special_adapter", "implemented_unverified", "source_only",
                [f"Routed Retail ERP surface {route}"],
                "Routed surface exists; browser/role verification pending.")

    # 2. Internal component features (never routed).
    if ftype in INTERNAL_FEATURE_TYPES:
        return ("internal", "internal", "n/a", [],
                f"{ftype} is a component of its parent, not an independent user route.")

    # 3. Platform/technical modules with no wholesale user destination.
    if priority == "internal":
        return ("internal", "internal", "n/a", [],
                "Platform/technical capability; owned by Frappe Desk, not a wholesale route.")

    # 5. Not-required modules.
    if priority == "not_required":
        return ("not_required", "not_required", "n/a", [],
                "Outside the stated wholesale importing/selling scope; ERPNext Desk retains it.")

    # 6. Document actions (mapped-document transitions).
    if ftype == "document_action":
        parent = feature.get("parent_feature") or feature.get("doctype")
        if parent in HANDCRAFTED_DOCTYPES:
            return ("special_adapter", "implemented_unverified", "source_only",
                    [f"Mapped action on {parent}"],
                    "Allowlisted mapped-document action exists; state/role/duplicate tests pending.")
        return ("unavailable_with_reason", "unavailable_with_reason", "n/a", [],
                f"Pending implementation ({priority}); standard Desk mapping remains source of truth.")

    # 7. Reports without a route.
    if ftype == "report":
        return ("generated_report", "unavailable_with_reason", "n/a", [],
                f"Not yet adapted ({priority}); runs in Desk. Candidate for the report engine.")

    # 8. Visual (workspace/dashboard/chart/number card).
    if ftype in VISUAL_TYPES:
        return ("generated_dashboard", "unavailable_with_reason", "n/a", [],
                f"Not yet adapted ({priority}); Desk workspace/dashboard remains source of truth.")

    # 9. Remaining in-scope DocTypes / pages -> planned, honestly unavailable.
    return ("unavailable_with_reason", "unavailable_with_reason", "n/a", [],
            f"Pending implementation ({priority}); standard Desk remains the source of truth.")


def build_parity_registry() -> dict:
    """Build the authoritative registry from the canonical inventory (read-only)."""
    data = json.loads(_canonical_path().read_text(encoding="utf-8"))
    entries = []
    for f in data["features"]:
        if not f.get("user_facing"):
            continue
        priority = _priority_for(f)
        strategy, status, vlevel, evidence, note = _strategy_and_status(f, priority)
        entries.append({
            "feature_key": f["feature_id"],
            "source_app": f.get("application"),
            "module": f.get("module"),
            "capability_type": f.get("feature_type"),
            "source_name": f.get("name"),
            "action_name": f.get("name") if f.get("feature_type") == "document_action" else None,
            "parent_feature": f.get("parent_feature"),
            "business_priority": priority,
            "implementation_strategy": strategy,
            "retail_erp_route": f.get("current_custom_route"),
            "backend_handler": None,
            "permission_rule": "standard_frappe_document_permissions",
            "status": status,
            "verification_level": vlevel,
            "evidence": evidence,
            "notes": note,
            "blocking_reason": None,
        })
    return {
        "schema": "retail-erp-parity-registry/1",
        "source_fingerprint": data.get("inventory_fingerprint"),
        "site": data.get("site"),
        "entry_count": len(entries),
        "entries": entries,
    }


def registry_summary(registry: dict) -> dict:
    entries = registry["entries"]
    by_status = Counter(e["status"] for e in entries)
    by_priority = Counter(e["business_priority"] for e in entries)
    by_strategy = Counter(e["implementation_strategy"] for e in entries)
    implemented = sum(by_status[s] for s in IMPLEMENTED_STATUSES)
    return {
        "entry_count": len(entries),
        "implemented_any": implemented,
        "by_status": dict(sorted(by_status.items())),
        "by_priority": dict(sorted(by_priority.items())),
        "by_strategy": dict(sorted(by_strategy.items())),
    }


def validate_parity_registry(registry: dict | None = None) -> dict:
    """Enforce the honesty contract. Returns {'status': 'pass'|'fail', 'errors': [...]}."""
    registry = registry or build_parity_registry()
    entries = registry["entries"]
    errors: list[str] = []

    # Coverage: every user-facing feature must be present exactly once.
    data = json.loads(_canonical_path().read_text(encoding="utf-8"))
    uf_keys = {f["feature_id"] for f in data["features"] if f.get("user_facing")}
    reg_keys = [e["feature_key"] for e in entries]
    key_counts = Counter(reg_keys)
    dupes = [k for k, n in key_counts.items() if n > 1]
    if dupes:
        errors.append(f"duplicate feature keys: {len(dupes)} (e.g. {dupes[:3]})")
    missing = uf_keys - set(reg_keys)
    if missing:
        errors.append(f"user-facing features with no registry entry: {len(missing)} (e.g. {sorted(missing)[:3]})")
    extra = set(reg_keys) - uf_keys
    if extra:
        errors.append(f"registry entries not user-facing in inventory: {len(extra)}")

    for e in entries:
        k = e["feature_key"]
        if e["implementation_strategy"] not in STRATEGIES:
            errors.append(f"{k}: unknown strategy {e['implementation_strategy']!r}")
        if e["status"] not in STATUSES:
            errors.append(f"{k}: unknown status {e['status']!r}")
        if e["business_priority"] not in PRIORITIES:
            errors.append(f"{k}: unknown priority {e['business_priority']!r}")
        if e["status"] == "verified_complete" and not e.get("evidence"):
            errors.append(f"{k}: verified_complete without evidence")
        # A bare route must never be counted as verified_complete.
        if e["status"] == "verified_complete" and e.get("verification_level") in {None, "route_only", "n/a"}:
            errors.append(f"{k}: verified_complete requires behavioural verification_level")
        # Routed entries must not silently be 'unavailable', 'not_required' or 'internal'.
        if e["retail_erp_route"] and e["status"] in {"unavailable_with_reason", "not_required", "internal"}:
            errors.append(f"{k}: has route but status {e['status']}")

    return {"status": "fail" if errors else "pass", "error_count": len(errors), "errors": errors[:50]}


def _summary_markdown(registry: dict, summ: dict, val: dict) -> str:
    prio_meaning = {
        "P0_go_live": "Blocks the fixed wholesale go-live flow",
        "P1_required": "Required before client go-live",
        "P2_important": "Important, not day-one blocking",
        "P3_optional": "Optional / after go-live",
        "not_required": "Outside the wholesale importing/selling scope",
        "internal": "Technical component, not a user route",
    }
    status_meaning = {
        "verified_complete": "Real implementation + behavioural evidence",
        "implemented_unverified": "Implemented, lacks browser/role/business verification",
        "generated_provisional": "Generic engine exposes it; specialised behaviour unverified",
        "special_adapter": "Dedicated adapter (e.g. mapped-document action)",
        "blocked": "Cannot complete without approval/credentials/packages",
        "unavailable_with_reason": "Inventoried, intentionally not yet available (planned)",
        "not_required": "Not needed for this business",
        "internal": "Technical/internal, no user route required",
    }
    L = ["# Authoritative Parity Registry Summary (Stage 2)", ""]
    L.append(f"- Source inventory fingerprint: `{registry['source_fingerprint']}`")
    L.append(f"- Registry entries (one per user-facing feature): **{summ['entry_count']}**")
    L.append(f"- Validation: **{val['status'].upper()}** ({val['error_count']} errors)")
    L.append(f"- Implemented in some form (custom/provisional/adapter/unverified): **{summ['implemented_any']}**")
    L.append("")
    L.append("> A route alone is never counted as completion. `unavailable_with_reason`, "
             "`not_required` and `internal` are NOT implemented functionality.")
    L.append("")
    L.append("## By status")
    L.append("")
    L.append("| Status | Meaning | Count |")
    L.append("|---|---|---:|")
    for s, n in summ["by_status"].items():
        L.append(f"| {s} | {status_meaning.get(s, '')} | {n} |")
    L.append("")
    L.append("## By business priority")
    L.append("")
    L.append("| Priority | Meaning | Count |")
    L.append("|---|---|---:|")
    for p, n in summ["by_priority"].items():
        L.append(f"| {p} | {prio_meaning.get(p, '')} | {n} |")
    L.append("")
    L.append("## By implementation strategy")
    L.append("")
    L.append("| Strategy | Count |")
    L.append("|---|---:|")
    for st, n in summ["by_strategy"].items():
        L.append(f"| {st} | {n} |")
    L.append("")
    L.append("## Reproduce / validate")
    L.append("")
    L.append("```bash")
    L.append("bench --site site1.local execute my_store_ui.audit.parity_registry.generate")
    L.append("bench --site site1.local execute my_store_ui.audit.parity_registry.validate_parity_registry")
    L.append("```")
    L.append("")
    return "\n".join(L) + "\n"


def generate() -> dict:
    """Write the authoritative registry snapshot + summary under docs/full-parity/inventory/."""
    registry = build_parity_registry()
    val = validate_parity_registry(registry)
    summ = registry_summary(registry)
    out = _canonical_path().parent / "full-parity" / "inventory"
    out.mkdir(parents=True, exist_ok=True)
    (out / "current_registry.json").write_text(
        json.dumps(registry, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
    )
    (out / "parity_registry_summary.md").write_text(_summary_markdown(registry, summ, val), encoding="utf-8")
    return {"validation": val["status"], "error_count": val["error_count"], "summary": summ}
