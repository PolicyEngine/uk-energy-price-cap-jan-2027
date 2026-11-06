import { cellValue } from "../utils/dataHelpers";
import { formatGbp, formatPct } from "../utils/format";

const METHOD_LABELS = {
  direct_debit: "Direct Debit",
  standard_credit: "Standard Credit",
  prepayment: "Prepayment",
  economy_7_direct_debit: "Economy 7 (Direct Debit)",
};

function formatBn(value) {
  if (value === null || value === undefined) return "withheld";
  const s = value < 0 ? "−" : value > 0 ? "+" : "";
  return `${s}£${Math.abs(value).toFixed(1)}bn`;
}

/** Headline tiles for the chosen scenario, and the levels by payment method now. */
export default function CapTiles({ cap, scenario, summary }) {
  const now = cap.payment_methods[cap.current_period];
  const change = scenario.direct_debit - now.direct_debit;
  return (
    <section className="space-y-4" aria-label="The cap">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="metric-card" data-testid="tile-cap">
          <p className="eyebrow text-slate-500">Typical bill, Jan to Mar 2027</p>
          <p className="text-3xl font-bold">{formatGbp(scenario.direct_debit)}</p>
          <p className="text-sm text-slate-600">{scenario.label}</p>
        </div>
        <div className="metric-card" data-testid="tile-change">
          <p className="eyebrow text-slate-500">Change on Oct to Dec 2026</p>
          <p className="text-3xl font-bold">{formatGbp(change, { sign: true })}</p>
          <p className="text-sm text-slate-600">{formatPct(scenario.change_pct)} on October to December 2026</p>
        </div>
        <div className="metric-card" data-testid="tile-total">
          <p className="eyebrow text-slate-500">All households in the cap</p>
          <p className="text-3xl font-bold">{formatBn(cellValue(summary?.total_change_gbp_bn))}</p>
          <p className="text-sm text-slate-600">Change in energy spend, £ a year</p>
        </div>
        <div className="metric-card" data-testid="tile-households">
          <p className="eyebrow text-slate-500">Households in the cap</p>
          <p className="text-3xl font-bold">
            {cellValue(summary?.households_in_cap_m) === null ? "withheld" : `${cellValue(summary.households_in_cap_m).toFixed(1)}m`}
          </p>
          <p className="text-sm text-slate-600">
            Average change {formatGbp(cellValue(summary?.avg_change_gbp), { sign: true })} a year
          </p>
        </div>
      </div>
      <div className="panel">
        <h3 className="mb-2 text-lg font-semibold">Cap levels by payment method, October to December 2026</h3>
        <table className="data-table compact" data-testid="payment-methods">
          <thead>
            <tr>
              <th>Payment method</th>
              <th>£ a year</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(now).map(([k, v]) => (
              <tr key={k}>
                <td>{METHOD_LABELS[k] ?? k}</td>
                <td>{formatGbp(v)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
