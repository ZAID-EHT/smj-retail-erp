export function formatDetailValue(value, type = "text", currency = "LKR") {
  if (value == null || value === "") return "—";
  if (type === "date") return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(`${value}T00:00:00`));
  if (type === "datetime") return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  if (type === "currency") {
    try { return new Intl.NumberFormat(undefined, { style: "currency", currency: currency || "LKR" }).format(Number(value)); }
    catch { return `${currency || ""} ${Number(value).toLocaleString()}`.trim(); }
  }
  if (type === "percent") return `${Number(value).toFixed(1)}%`;
  if (type === "number") return Number(value).toLocaleString();
  if (type === "boolean") return Number(value) ? "Yes" : "No";
  if (type === "enabled_status") return Number(value) ? "Disabled" : "Enabled";
  return String(value);
}

export function detailStatusClass(value, type = "status") {
  if (type === "enabled_status") return Number(value) ? "muted" : "green";
  const normalized = String(value || "").toLowerCase();
  if (["completed", "enabled", "paid", "submitted"].some((entry) => normalized.includes(entry))) return "green";
  if (["cancelled", "closed", "disabled"].some((entry) => normalized.includes(entry))) return "muted";
  if (["draft", "on hold", "unpaid", "overdue"].some((entry) => normalized.includes(entry))) return "orange";
  return "blue";
}
