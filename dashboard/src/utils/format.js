export function formatGbp(value, { sign = false } = {}) {
  if (value === null || value === undefined) return "withheld";
  const s = value < 0 ? "−" : sign && value > 0 ? "+" : "";
  return `${s}£${Math.abs(Math.round(value)).toLocaleString("en-GB")}`;
}

/** Pounds to the penny, as on a bill. */
export function formatGbpPence(value, { sign = false } = {}) {
  if (value === null || value === undefined) return "withheld";
  const s = value < 0 ? "−" : sign && value > 0 ? "+" : "";
  return `${s}£${Math.abs(value).toLocaleString("en-GB", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

/** Axis tick in pounds: £0, £550, £1,100. */
export function formatGbpTick(value) {
  return formatGbp(value);
}

export function formatPctTick(value) {
  if (value === null || value === undefined) return "";
  return `${value}%`;
}

export function formatMillions(value) {
  if (value === null || value === undefined) return "not computable";
  if (Math.abs(value) >= 1000) return `£${(value / 1000).toFixed(1)}bn`;
  return `£${Math.round(value).toLocaleString("en-GB")}m`;
}

export function formatPct(value, digits = 1) {
  if (value === null || value === undefined) return "withheld";
  const s = value < 0 ? "−" : value > 0 ? "+" : "";
  return `${s}${Math.abs(value).toFixed(digits)}%`;
}

export function toCsv(rows) {
  if (!rows.length) return "";
  const keys = Object.keys(rows[0]);
  const cell = (v) => (v === null || v === undefined ? "" : String(v).includes(",") ? `"${v}"` : String(v));
  return [keys.join(","), ...rows.map((r) => keys.map((k) => cell(r[k])).join(","))].join("\n");
}
