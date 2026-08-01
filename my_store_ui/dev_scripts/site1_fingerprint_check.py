"""Read-only integrity fingerprint for the protected site.

Compares the current document counts against the fingerprint recorded at the start
of the mission. Never writes anything.
"""

from __future__ import annotations

import hashlib
import json

import frappe

DOCTYPES = (
	"Batch", "Customer", "Delivery Note", "GL Entry", "Item", "Payment Entry",
	"Purchase Invoice", "Purchase Order", "Purchase Receipt", "Sales Invoice",
	"Sales Order", "Stock Ledger Entry", "User",
)
EXPECTED_SHA = "f51fedb5a9ac68e27b1515daee5cdf2f90490a22c07925960dd0acb4d123d9c3"


def run():
	counts = {}
	for doctype in DOCTYPES:
		try:
			counts[doctype] = frappe.db.count(doctype)
		except Exception:
			counts[doctype] = "n/a"
	blob = json.dumps(counts, sort_keys=True)
	sha = hashlib.sha256(blob.encode()).hexdigest()
	print("FINGERPRINT_JSON", blob)
	print("FINGERPRINT_SHA", sha)
	print("MATCHES_BASELINE", sha == EXPECTED_SHA)
