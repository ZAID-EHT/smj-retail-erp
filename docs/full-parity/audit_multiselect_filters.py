"""Cross-check every REPORT_FILTERS entry against the real erpnext report
source, to find filters that are list-parsed server-side but NOT declared in
MULTISELECT_REPORT_FILTER_FIELDS (=> would crash / misbehave when passed a
plain string from the Retail ERP filter form)."""
import re, sys
from pathlib import Path

sys.path.insert(0, "apps/my_store_ui")
from my_store_ui.services.priority_registry import REPORT_FILTERS
from my_store_ui.priority_pages import MULTISELECT_REPORT_FILTER_FIELDS

ERP = Path("apps/erpnext/erpnext")
report_py = {}
for p in ERP.rglob("report/*/*.py"):
    if p.stem.startswith("test_") or p.stem == "__init__":
        continue
    report_py.setdefault(p.stem, p)

SHARED = (ERP / "accounts/report/financial_statements.py").read_text()

def scrub(name):
    return name.lower().replace(" ", "_").replace("-", "_").replace("&", "and").replace("(", "").replace(")", "")

problems = []
for report, filters in sorted(REPORT_FILTERS.items()):
    path = report_py.get(scrub(report))
    if not path:
        continue
    src = path.read_text()
    combined = src + (SHARED if "financial_statements import" in src else "")
    declared = MULTISELECT_REPORT_FILTER_FIELDS.get(report, set())
    for f in filters:
        listy = (
            re.search(rf"filters\.{f}\s*=\s*frappe\.parse_json", combined)
            or re.search(rf'parse_json\(filters\.get\(\s*[\'"]{f}[\'"]', combined)
            or (f in ("cost_center",) and "get_cost_centers_with_children" in combined)
        )
        if listy and f not in declared:
            problems.append((report, f))

if problems:
    print("MISSING from MULTISELECT_REPORT_FILTER_FIELDS (list-parsed server-side):")
    for r, f in problems:
        print(f"  {r:45s} {f}")
else:
    print("no gaps found")
