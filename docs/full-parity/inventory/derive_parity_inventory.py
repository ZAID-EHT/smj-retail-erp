#!/usr/bin/env python3
"""Derive full-parity/inventory/* files from the canonical feature inventory.

Read-only. Run AFTER regenerating the canonical inventory:

    cd /home/zaidh/frappe-bench
    bench --site site1.local execute my_store_ui.audit.feature_inventory.generate_complete_inventory
    python3 apps/my_store_ui/docs/full-parity/inventory/derive_parity_inventory.py

Emits, next to this script:
  complete_inventory.json   every feature, key fields only (trimmed, complete row set)
  current_registry.json     features that currently have a custom route (mapped today)
  strict_audit_before.json  strict-audit snapshot + counts of interest
  unmapped_before.json      every user-facing feature without a custom route
  inventory_summary.md      human-readable summary

This does NOT mutate the site or the canonical JSON. It only reshapes the
canonical output into reviewable capture files for the parity mission.
"""
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parents[2]  # docs/full-parity/inventory -> app root
CANON = APP / "docs" / "erpnext-v15-complete-inventory.json"
OUT = HERE

NOW = datetime.now().strftime("%Y-%m-%d %H:%M")

data = json.loads(CANON.read_text(encoding="utf-8"))
features = data["features"]
counts = data["counts"]
audit = data["automated_audit"]

SLIM_FIELDS = [
    "feature_id", "application", "module", "feature_type", "name",
    "doctype", "report", "page", "parent_feature", "classification",
    "user_facing", "current_custom_route", "standard_desk_route",
    "completion_status", "test_status", "remaining_desk_dependency",
    "exclusion_reason",
]


def slim(f):
    return {k: f.get(k) for k in SLIM_FIELDS}


complete = {
    "captured_at": NOW,
    "site": data.get("site"),
    "schema_version": data.get("schema_version"),
    "source": "docs/erpnext-v15-complete-inventory.json",
    "inventory_fingerprint": data.get("inventory_fingerprint"),
    "counts": counts,
    "features": [slim(f) for f in features],
}
(OUT / "complete_inventory.json").write_text(
    json.dumps(complete, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
)

# NOTE: the authoritative registry (current_registry.json) is owned by
# my_store_ui.audit.parity_registry.generate. Here we only snapshot which
# features currently carry a route, as `currently_routed.json`.
mapped = [slim(f) for f in features if f.get("current_custom_route")]
(OUT / "currently_routed.json").write_text(
    json.dumps({
        "captured_at": NOW,
        "definition": "A feature is 'currently routed' iff the canonical audit assigned it a current_custom_route.",
        "routed_count": len(mapped),
        "features": sorted(mapped, key=lambda x: (x["application"], x["module"], x["name"])),
    }, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
)

(OUT / "strict_audit_before.json").write_text(
    json.dumps({
        "captured_at": NOW,
        "site": data.get("site"),
        "inventory_fingerprint": data.get("inventory_fingerprint"),
        "status": audit["status"],
        "failure_counts": audit["failure_counts"],
        "counts_of_interest": {
            "user_facing_features": counts["user_facing_features"],
            "system_internal_exclusions": counts["system_internal_exclusions"],
            "features_total": counts["features_total"],
            "mapped_user_facing": counts["user_facing_features"] - audit["failure_counts"]["unmapped_user_facing"],
            "unmapped_user_facing": audit["failure_counts"]["unmapped_user_facing"],
            "generic_engine_features": counts["generic_engine_features"],
            "specialized_interfaces": counts["specialized_interfaces"],
        },
    }, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
)

unmapped = [slim(f) for f in features if f.get("user_facing") and not f.get("current_custom_route")]
(OUT / "unmapped_before.json").write_text(
    json.dumps({
        "captured_at": NOW,
        "unmapped_user_facing_count": len(unmapped),
        "by_feature_type": dict(sorted(Counter(f["feature_type"] for f in unmapped).items())),
        "by_module": dict(sorted(Counter(f["module"] for f in unmapped).items(), key=lambda kv: -kv[1])),
        "features": sorted(unmapped, key=lambda x: (x["application"], x["module"], x["feature_type"], x["name"])),
    }, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8"
)

uf_by_type = Counter(f["feature_type"] for f in features if f["user_facing"])
uf_by_app = Counter(f["application"] for f in features if f["user_facing"])
uf_by_class = Counter(f["classification"] for f in features if f["user_facing"])
by_module = dict(sorted(Counter(f["module"] for f in unmapped).items(), key=lambda kv: -kv[1]))
class_labels = {
    "A": "Generic list/detail/form engine", "B": "Specialized transaction interface",
    "C": "Specialized visual view", "D": "Report engine", "E": "Administrative interface",
    "F": "Safe embedded integration", "G": "System-internal (not user-facing)",
}
L = []
L.append("# Full-Parity Inventory Summary (Stage 1)")
L.append("")
L.append(f"- Captured: {NOW}")
L.append(f"- Site: `{data.get('site')}`")
L.append("- Canonical source: `docs/erpnext-v15-complete-inventory.json`")
L.append(f"- Inventory fingerprint: `{data.get('inventory_fingerprint')}`")
L.append("")
L.append("## Headline counts")
L.append("")
L.append("| Metric | Value |")
L.append("|---|---:|")
L.append(f"| Total atomic features | {counts['features_total']} |")
L.append(f"| User-facing features | {counts['user_facing_features']} |")
L.append(f"| System-internal exclusions | {counts['system_internal_exclusions']} |")
L.append(f"| Currently mapped (has custom route) | {len(mapped)} |")
L.append(f"| Unmapped user-facing | {audit['failure_counts']['unmapped_user_facing']} |")
L.append(f"| Strict route coverage | {100.0*len(mapped)/counts['user_facing_features']:.2f}% |")
L.append(f"| Generic engine candidates (class A) | {counts['generic_engine_features']} |")
L.append(f"| Specialised interfaces (class B+C) | {counts['specialized_interfaces']} |")
L.append(f"| Installed non-core app features | {counts['installed_app_features']} |")
L.append(f"| Strict audit status | **{audit['status'].upper()}** |")
L.append("")
L.append("## User-facing features by application")
L.append("")
L.append("| Application | User-facing features |")
L.append("|---|---:|")
for app, n in uf_by_app.most_common():
    L.append(f"| {app} | {n} |")
L.append("")
L.append("## User-facing features by type")
L.append("")
L.append("| Feature type | Count |")
L.append("|---|---:|")
for t, n in sorted(uf_by_type.items(), key=lambda kv: -kv[1]):
    L.append(f"| {t} | {n} |")
L.append("")
L.append("## User-facing features by implementation class")
L.append("")
L.append("| Class | Meaning | User-facing count |")
L.append("|---|---|---:|")
for code in "ABCDEFG":
    L.append(f"| {code} | {class_labels[code]} | {uf_by_class.get(code, 0)} |")
L.append("")
L.append("## Top modules by unmapped user-facing features")
L.append("")
L.append("| Module | Unmapped |")
L.append("|---|---:|")
for mod, n in list(by_module.items())[:25]:
    L.append(f"| {mod or '(none)'} | {n} |")
L.append("")
(OUT / "inventory_summary.md").write_text("\n".join(L) + "\n", encoding="utf-8")

print(f"mapped={len(mapped)} unmapped={len(unmapped)} user_facing={counts['user_facing_features']} fingerprint={data.get('inventory_fingerprint')[:12]}")
