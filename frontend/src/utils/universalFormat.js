export function formatUniversalValue(value, column, currency = "") {
  if (value === null || value === undefined || value === "") return "—";
  if (column?.fieldtype === "Check") return Number(value) ? "Yes" : "No";
  if (["Currency", "Float", "Percent", "Int", "Duration", "Rating"].includes(column?.fieldtype)) {
    const formatted = new Intl.NumberFormat(undefined, { minimumFractionDigits: column.fieldtype === "Int" ? 0 : 0, maximumFractionDigits: column.fieldtype === "Int" ? 0 : 2 }).format(Number(value));
    return column.fieldtype === "Percent" ? `${formatted}%` : column.fieldtype === "Currency" && currency ? `${currency} ${formatted}` : formatted;
  }
  if (["Date", "Datetime"].includes(column?.fieldtype)) {
    const date = new Date(column.fieldtype === "Date" ? `${value}T00:00:00` : value);
    return Number.isNaN(date.getTime()) ? String(value) : new Intl.DateTimeFormat(undefined, column.fieldtype === "Date" ? { dateStyle: "medium" } : { dateStyle: "medium", timeStyle: "short" }).format(date);
  }
  return String(value);
}

export function isBadgeColumn(column) {
  return column?.fieldtype === "Check" || ["status", "workflow_state", "disabled", "enabled", "is_group", "selling", "buying"].includes(column?.fieldname);
}
