import { formatGbp, formatPct } from "../utils/format";

const METHOD_LABELS = {
  direct_debit: "Direct Debit",
  standard_credit: "Standard Credit",
  prepayment: "Prepayment",
  economy_7_direct_debit: "Economy 7 (Direct Debit)",
};

/** The cap level for the chosen scenario, and the levels by payment method now. */
export default function CapTiles({ cap, scenario }) {
  const now = cap.payment_methods[cap.current_period];
  const change = scenario.direct_debit - now.direct_debit;
  return (
    <section className="space-y-4" aria-label="The cap">
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="metric-card" data-testid="tile-cap">
          <p className="eyebrow text-slate-500">Typical bill, Jan to Mar 2027</p>
          <p className="text-3xl font-bold">{formatGbp(scenario.direct_debit)}</p>
          <p className="text-sm text-slate-600">{scenario.label}</p>
        </div>
        <div className="metric-card" data-testid="tile-change">
          <p className="eyebrow text-slate-500">Change from Oct to Dec 2026</p>
          <p className="text-3xl font-bold">{formatGbp(change, { sign: true })}</p>
          <p className="text-sm text-slate-600">{formatPct(scenario.change_pct)} a year</p>
        </div>
        <div className="metric-card">
          <p className="eyebrow text-slate-500">Typical use</p>
          <p className="text-3xl font-bold">2,500 / 9,500 kWh</p>
          <p className="text-sm text-slate-600">Electricity / gas, Direct Debit, dual fuel</p>
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
