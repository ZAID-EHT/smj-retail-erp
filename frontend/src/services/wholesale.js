import { UniversalApiError } from "@/services/universal.js";

const PREFIX = "/api/method/my_store_ui.wholesale.";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary */ }
  return payload?.message?.message || payload?.message || fallback;
}

async function call(method, params = {}, { signal, httpMethod = "GET" } = {}) {
  const isGet = httpMethod === "GET";
  const query = new URLSearchParams(
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null && value !== "")
      .map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : value]),
  );
  const response = await fetch(`${PREFIX}${method}${isGet && query.size ? `?${query}` : ""}`, {
    method: httpMethod,
    credentials: "same-origin",
    cache: "no-store",
    signal,
    headers: isGet ? {} : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
    body: isGet ? undefined : JSON.stringify(params),
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    throw new UniversalApiError(message(payload, "The request could not be completed."), response, payload);
  }
  return payload.message;
}

export const getWholesaleTransactions = (params, signal) =>
  call("register.get_wholesale_transactions", params, { signal });
export const getTransactionTimeline = (salesOrder, signal) =>
  call("register.get_transaction_timeline", { sales_order: salesOrder }, { signal });
export const getCustomerCreditStatus = (customer, company, signal) =>
  call("credit.get_customer_credit_status", { customer, company }, { signal });
export const getStockAvailability = (itemCode, warehouse, company, signal) =>
  call("reservation.get_stock_availability", { item_code: itemCode, warehouse, company }, { signal });

export const getUnreconciledEntries = (params, signal) =>
  call("payment_reconciliation_api.get_unreconciled_entries", params, { signal, httpMethod: "POST" });
export const previewReconciliationAllocation = (params, signal) =>
  call("payment_reconciliation_api.preview_allocation", params, { signal, httpMethod: "POST" });
export const reconcilePayments = (params, signal) =>
  call("payment_reconciliation_api.reconcile", params, { signal, httpMethod: "POST" });
export const searchReconciliationCompany = (txt, signal) =>
  call("payment_reconciliation_api.search_company", { txt }, { signal });
export const searchReconciliationParty = (partyType, txt, signal) =>
  call("payment_reconciliation_api.search_party", { party_type: partyType, txt }, { signal });

export const searchBankAccount = (txt, company, signal) =>
  call("bank_reconciliation_api.search_bank_account", { txt, company }, { signal });
export const searchBankReconciliationParty = (partyType, txt, signal) =>
  call("bank_reconciliation_api.search_party", { party_type: partyType, txt }, { signal });
export const searchAccount = (txt, company, signal) =>
  call("bank_reconciliation_api.search_account", { txt, company }, { signal });
export const searchModeOfPayment = (txt, signal) =>
  call("bank_reconciliation_api.search_mode_of_payment", { txt }, { signal });
export const getBankReconciliationSummary = (params, signal) =>
  call("bank_reconciliation_api.get_summary", params, { signal, httpMethod: "POST" });
export const getBankTransactionMatches = (params, signal) =>
  call("bank_reconciliation_api.get_matches", params, { signal, httpMethod: "POST" });
export const updateBankTransactionReference = (params, signal) =>
  call("bank_reconciliation_api.update_transaction_reference", params, { signal, httpMethod: "POST" });
export const reconcileBankTransaction = (params, signal) =>
  call("bank_reconciliation_api.reconcile_transaction", params, { signal, httpMethod: "POST" });
export const unreconcileBankTransaction = (params, signal) =>
  call("bank_reconciliation_api.unreconcile_transaction", params, { signal, httpMethod: "POST" });
export const previewBankPaymentEntry = (params, signal) =>
  call("bank_reconciliation_api.preview_payment_entry", params, { signal, httpMethod: "POST" });
export const confirmBankPaymentEntry = (params, signal) =>
  call("bank_reconciliation_api.confirm_payment_entry", params, { signal, httpMethod: "POST" });
export const previewBankJournalEntry = (params, signal) =>
  call("bank_reconciliation_api.preview_journal_entry", params, { signal, httpMethod: "POST" });
export const confirmBankJournalEntry = (params, signal) =>
  call("bank_reconciliation_api.confirm_journal_entry", params, { signal, httpMethod: "POST" });
export const autoReconcileBankTransactions = (params, signal) =>
  call("bank_reconciliation_api.auto_reconcile", params, { signal, httpMethod: "POST" });
