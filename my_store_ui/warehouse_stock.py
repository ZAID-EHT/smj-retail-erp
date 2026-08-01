"""Warehouse drill-down: item-wise and batch-wise stock inside one warehouse.

ACCOUNT CREATION.docx asks to click a warehouse and view the individual stock
inside it, batch-wise and item-wise, filtered by a date range and other criteria.

Every figure comes from standard ERPNext sources (Bin, Batch, Stock Ledger Entry)
through permission-aware reads. No separate stock total is maintained.
"""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import cint, flt, nowdate

MAX_ROWS = 500

STOCK_STATUS = ("all", "in_stock", "low_stock", "out_of_stock")
LOW_STOCK_THRESHOLD = 20


def _require_login() -> None:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication is required."), frappe.AuthenticationError)


def _check_warehouse(warehouse: str) -> dict:
	row = frappe.db.get_value(
		"Warehouse", warehouse, ["name", "company", "is_group", "disabled"], as_dict=True
	)
	if not row:
		frappe.throw(_("Warehouse {0} does not exist.").format(warehouse), frappe.ValidationError)
	if not frappe.has_permission("Warehouse", "read", doc=warehouse):
		frappe.throw(_("You do not have access to this warehouse."), frappe.PermissionError)
	return row


@frappe.whitelist(methods=["GET"])
def get_warehouse_stock(warehouse: str, search: str = "", item_group: str = "",
                        stock_status: str = "all", from_date: str | None = None,
                        to_date: str | None = None, batch: str = "", limit: int = 100):
	"""Item-wise stock in one warehouse, with Actual / Reserved / Available."""
	_require_login()
	info = _check_warehouse(warehouse)
	if stock_status not in STOCK_STATUS:
		frappe.throw(
			_("Invalid stock status. Allowed: {0}.").format(", ".join(STOCK_STATUS)),
			frappe.ValidationError,
		)
	if from_date and to_date and from_date > to_date:
		frappe.throw(_("The From date must be on or before the To date."), frappe.ValidationError)
	limit = min(max(cint(limit) or 100, 1), MAX_ROWS)

	if not frappe.has_permission("Bin", "read"):
		frappe.throw(_("You do not have access to stock levels."), frappe.PermissionError)

	filters = {"warehouse": warehouse}
	bins = frappe.get_all(
		"Bin", filters=filters,
		fields=["item_code", "actual_qty", "reserved_qty", "reserved_stock",
		        "projected_qty", "stock_value", "valuation_rate"],
		limit_page_length=0,
	)

	# "Recently added" is a Stock Ledger question, so restrict by the items that
	# actually moved in the window rather than filtering Bin, which has no date.
	moved_items = None
	if from_date or to_date:
		ledger_filters = {"warehouse": warehouse, "is_cancelled": 0}
		if from_date and to_date:
			ledger_filters["posting_date"] = ["between", [from_date, to_date]]
		elif from_date:
			ledger_filters["posting_date"] = [">=", from_date]
		else:
			ledger_filters["posting_date"] = ["<=", to_date]
		moved_items = {
			r["item_code"]
			for r in frappe.get_all(
				"Stock Ledger Entry", filters=ledger_filters, fields=["item_code"],
				limit_page_length=0, distinct=True,
			)
		}

	item_names = {}
	groups = {}
	codes = [b["item_code"] for b in bins]
	if codes:
		for row in frappe.get_all(
			"Item", filters={"name": ["in", codes]},
			fields=["name", "item_name", "item_group", "stock_uom", "custom_carton_qty"],
			limit_page_length=0,
		):
			item_names[row["name"]] = row

	search = (search or "").strip().lower()
	rows = []
	for entry in bins:
		code = entry["item_code"]
		if moved_items is not None and code not in moved_items:
			continue
		meta = item_names.get(code) or {}
		if item_group and meta.get("item_group") != item_group:
			continue
		if search and search not in code.lower() and search not in (meta.get("item_name") or "").lower():
			continue
		actual = flt(entry.get("actual_qty"))
		reserved = flt(entry.get("reserved_stock")) or flt(entry.get("reserved_qty"))
		available = actual - reserved
		if stock_status == "out_of_stock" and available > 0:
			continue
		if stock_status == "in_stock" and available <= 0:
			continue
		if stock_status == "low_stock" and not (0 < available <= LOW_STOCK_THRESHOLD):
			continue
		rows.append({
			"item_code": code,
			"item_name": meta.get("item_name") or code,
			"item_group": meta.get("item_group"),
			"stock_uom": meta.get("stock_uom"),
			"carton_qty": flt(meta.get("custom_carton_qty")),
			"actual_qty": actual,
			"reserved_qty": reserved,
			"available_to_sell": available,
			"stock_value": flt(entry.get("stock_value")),
			"valuation_rate": flt(entry.get("valuation_rate")),
		})
		if code in groups:
			continue
		groups[meta.get("item_group")] = True

	rows.sort(key=lambda r: (-r["actual_qty"], r["item_code"]))
	total_rows = len(rows)
	rows = rows[:limit]

	return {
		"warehouse": warehouse,
		"company": info.company,
		"is_group": bool(info.is_group),
		"disabled": bool(info.disabled),
		"rows": rows,
		"total_rows": total_rows,
		"truncated": total_rows > len(rows),
		"item_groups": sorted([g for g in groups if g]),
		"stock_status_options": list(STOCK_STATUS),
		"totals": {
			"items": total_rows,
			"actual_qty": sum(r["actual_qty"] for r in rows),
			"reserved_qty": sum(r["reserved_qty"] for r in rows),
			"available_to_sell": sum(r["available_to_sell"] for r in rows),
			"stock_value": sum(r["stock_value"] for r in rows),
		},
		"filters": {
			"search": search, "item_group": item_group, "stock_status": stock_status,
			"from_date": from_date, "to_date": to_date, "batch": batch,
		},
	}


def _batch_items_in(warehouse: str) -> list[str]:
	"""Batch-managed items that currently hold stock in this warehouse."""
	rows = frappe.get_all(
		"Bin", filters={"warehouse": warehouse, "actual_qty": [">", 0]},
		fields=["item_code"], limit_page_length=0,
	)
	codes = [r["item_code"] for r in rows]
	if not codes:
		return []
	return frappe.get_all(
		"Item", filters={"name": ["in", codes], "has_batch_no": 1}, pluck="name",
		limit_page_length=0,
	)


@frappe.whitelist(methods=["GET"])
def get_warehouse_batches(warehouse: str, item_code: str = "", from_date: str | None = None,
                          to_date: str | None = None, limit: int = 200):
	"""Batch-wise stock inside a warehouse, oldest batch first (FIFO order)."""
	_require_login()
	_check_warehouse(warehouse)
	if not frappe.has_permission("Batch", "read"):
		frappe.throw(_("You do not have access to batches."), frappe.PermissionError)
	if from_date and to_date and from_date > to_date:
		frappe.throw(_("The From date must be on or before the To date."), frappe.ValidationError)
	limit = min(max(cint(limit) or 200, 1), MAX_ROWS)

	# ERPNext v15 may hold the batch on the Stock Ledger Entry or inside a Serial
	# and Batch Bundle. Ask ERPNext's own allocator for current batch levels rather
	# than reading either storage directly -- it is the same source the FIFO
	# delivery allocation uses, so the two can never disagree.
	from erpnext.stock.doctype.serial_and_batch_bundle.serial_and_batch_bundle import (
		get_auto_batch_nos,
	)

	items = [item_code] if item_code else _batch_items_in(warehouse)
	ledger = []
	for code in items:
		try:
			available = get_auto_batch_nos(frappe._dict({
				"item_code": code, "warehouse": warehouse, "for_stock_levels": True,
			})) or []
		except Exception:
			frappe.log_error(title="Warehouse batch levels failed", message=frappe.get_traceback())
			continue
		for row in available:
			qty = flt(row.get("qty"))
			if qty > 0:
				ledger.append({"batch_no": row.get("batch_no"), "item_code": code, "qty": qty})

	batch_names = [r["batch_no"] for r in ledger if r.get("batch_no")]
	meta = {}
	if batch_names:
		for row in frappe.get_all(
			"Batch", filters={"name": ["in", batch_names]},
			fields=["name", "expiry_date", "manufacturing_date", "creation", "item"],
			limit_page_length=0,
		):
			meta[row["name"]] = row

	today = nowdate()
	rows = []
	for entry in ledger:
		qty = flt(entry.get("qty"))
		if qty <= 0:
			continue
		info = meta.get(entry["batch_no"]) or {}
		expiry = info.get("expiry_date")
		rows.append({
			"batch_no": entry["batch_no"],
			"item_code": entry["item_code"],
			"qty": qty,
			"expiry_date": str(expiry) if expiry else None,
			"expired": bool(expiry and str(expiry) < today),
			"created": str(info.get("creation") or ""),
		})

	# Oldest first: the same order the FIFO allocator consumes them.
	rows.sort(key=lambda r: (r["created"], r["batch_no"]))
	return {
		"warehouse": warehouse, "item_code": item_code or None,
		"rows": rows[:limit], "total_rows": len(rows),
		"total_qty": sum(r["qty"] for r in rows),
	}


@frappe.whitelist(methods=["GET"])
def get_warehouse_movements(warehouse: str, item_code: str = "", from_date: str | None = None,
                            to_date: str | None = None, limit: int = 100):
	"""Recent receipts, issues and transfers for a warehouse."""
	_require_login()
	_check_warehouse(warehouse)
	if not frappe.has_permission("Stock Ledger Entry", "read"):
		frappe.throw(_("You do not have access to stock movements."), frappe.PermissionError)
	if from_date and to_date and from_date > to_date:
		frappe.throw(_("The From date must be on or before the To date."), frappe.ValidationError)
	limit = min(max(cint(limit) or 100, 1), MAX_ROWS)

	filters = {"warehouse": warehouse, "is_cancelled": 0}
	if item_code:
		filters["item_code"] = item_code
	if from_date and to_date:
		filters["posting_date"] = ["between", [from_date, to_date]]
	elif from_date:
		filters["posting_date"] = [">=", from_date]
	elif to_date:
		filters["posting_date"] = ["<=", to_date]

	rows = frappe.get_all(
		"Stock Ledger Entry", filters=filters,
		fields=["posting_date", "item_code", "actual_qty", "qty_after_transaction",
		        "voucher_type", "voucher_no", "batch_no", "valuation_rate"],
		order_by="posting_date desc, creation desc", limit_page_length=limit,
	)
	return {
		"warehouse": warehouse,
		"rows": [
			{**r, "posting_date": str(r["posting_date"]),
			 "direction": "in" if flt(r["actual_qty"]) >= 0 else "out"}
			for r in rows
		],
		"count": len(rows),
	}
