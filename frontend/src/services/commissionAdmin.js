import { UniversalApiError } from "@/services/universal.js";

function message(payload, fallback) {
  try {
    const messages = JSON.parse(payload?._server_messages || "[]");
    if (messages.length) return JSON.parse(messages[0]).message || fallback;
  } catch { /* envelope shapes vary */ }
  return payload?.message?.message || payload?.message || fallback;
}

// Only an absent value is dropped. An empty string is a deliberate value -- a
// cleared filter means "all" -- so it must still reach the server.
function query(values) {
  return new URLSearchParams(
    Object.entries(values || {})
      .filter(([, value]) => value !== undefined && value !== null)
      .map(([key, value]) => [key, typeof value === "object" ? JSON.stringify(value) : String(value)]),
  );
}

async function call(module, method, params = {}, { signal, httpMethod = "GET" } = {}) {
  const isGet = httpMethod === "GET";
  const search = query(params);
  const response = await fetch(
    `/api/method/my_store_ui.${module}.${method}${isGet && search.size ? `?${search}` : ""}`,
    {
      method: httpMethod,
      credentials: "same-origin",
      cache: "no-store",
      signal,
      headers: isGet
        ? {}
        : { "Content-Type": "application/json", "X-Frappe-CSRF-Token": window.frappe?.csrf_token || "" },
      body: isGet ? undefined : JSON.stringify(params),
    },
  );
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.exc) {
    // Never surface a traceback; the server message is the human one.
    throw new UniversalApiError(message(payload, "The request could not be completed."), response, payload);
  }
  return payload.message;
}

const policy = (m, p, o) => call("commission_policy", m, p, o);
const period = (m, p, o) => call("commission_period", m, p, o);
const payout = (m, p, o) => call("commission_payout", m, p, o);
const POST = { httpMethod: "POST" };

/* ---- policy ---- */
export const listCommissionPolicies = (p, signal) => policy("list_commission_policies", p || {}, { signal });
export const getCommissionPolicy = (name, signal) => policy("get_commission_policy", { name: name || "" }, { signal });
export const saveCommissionPolicy = (payload, name) =>
  policy("save_commission_policy", { payload, name: name || "" }, POST);
export const approveCommissionPolicy = (name, note) =>
  policy("approve_commission_policy", { name, note: note || "" }, POST);
export const suspendCommissionPolicy = (name, reason) =>
  policy("suspend_commission_policy", { name, reason }, POST);
export const validateCommissionPolicy = (name, signal) =>
  policy("validate_commission_policy", { name }, { signal });
export const simulateCommissionPolicy = (p, signal) =>
  policy("simulate_commission_policy", p, { signal });
export const getCommissionPolicyStatus = (company, signal) =>
  policy("get_commission_policy_status", { company: company || "" }, { signal });

/* ---- periods ---- */
export const listCommissionPeriods = (p, signal) => period("list_commission_periods", p || {}, { signal });
export const getCommissionPeriod = (name, signal) => period("get_commission_period", { name }, { signal });
export const createCommissionPeriod = (p) => period("create_commission_period", p, POST);
export const prepareCommissionPeriod = (name) => period("prepare_commission_period", { name }, POST);
export const submitPeriodForReview = (name, comment) =>
  period("submit_period_for_review", { name, comment: comment || "" }, POST);
export const reviewCommissionPeriod = (name, comment) =>
  period("review_commission_period", { name, comment: comment || "" }, POST);
export const approveCommissionPeriod = (name, comment) =>
  period("approve_commission_period", { name, comment: comment || "" }, POST);
export const reopenCommissionPeriod = (name, reason) =>
  period("reopen_commission_period", { name, reason }, POST);
export const cancelCommissionPeriod = (name, reason) =>
  period("cancel_commission_period", { name, reason }, POST);
export const getPeriodApprovalChecks = (name, signal) =>
  period("get_period_approval_checks", { name }, { signal });
export const resolveCommissionException = (name, idx, resolution, note) =>
  period("resolve_commission_exception", { name, idx, resolution, note: note || "" }, POST);
export const requestCommissionAdjustment = (p) => period("request_commission_adjustment", p, POST);
export const approveCommissionAdjustment = (name, note) =>
  period("approve_commission_adjustment", { name, note: note || "" }, POST);
export const rejectCommissionAdjustment = (name, note) =>
  period("reject_commission_adjustment", { name, note }, POST);

/* ---- statements, payout, review, dashboard ---- */
export const listCommissionStatements = (p, signal) => payout("list_commission_statements", p, { signal });
export const getCommissionStatement = (p, signal) => payout("get_commission_statement", p, { signal });
export const prepareCommissionPayout = (period_) => payout("prepare_commission_payout", { period: period_ }, POST);
export const validateCommissionPayout = (name) => payout("validate_commission_payout", { name }, POST);
export const listCommissionPayouts = (p, signal) => payout("list_commission_payouts", p || {}, { signal });
export const getCommissionPayout = (name, signal) => payout("get_commission_payout", { name }, { signal });
export const postCommissionPayout = (name, confirmation) =>
  payout("post_commission_payout", { name, confirmation: confirmation || "" }, POST);
export const listHistoricalReview = (p, signal) =>
  payout("list_historical_commission_review", p || {}, { signal });
export const recordHistoricalDecision = (p) =>
  payout("record_historical_commission_decision", p, POST);
export const getCommissionDashboard = (company, signal) =>
  payout("get_commission_dashboard", { company: company || "" }, { signal });
