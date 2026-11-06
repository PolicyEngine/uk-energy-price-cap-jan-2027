import { cellValue } from "../utils/dataHelpers";

function pct(cell) {
  const v = cellValue(cell);
  return v === null || v === undefined ? "withheld" : `${v.toFixed(1)}%`;
}

/** Fuel stress proxy and whether the £100 covers the rise, for one scenario. */
export default function BillsSummary({ summary }) {
  if (!summary) return null;
  return (
    <section className="grid gap-4 sm:grid-cols-2" aria-label="Households under strain">
      <div className="metric-card" data-testid="tile-fuel-stress">
        <p className="eyebrow text-slate-500">Energy spend above 10% of net income</p>
        <p className="text-3xl font-bold">
          {pct(summary.energy_over_10pct_now_pct)} to {pct(summary.energy_over_10pct_then_pct)}
        </p>
        <p className="text-sm text-slate-600">
          Share of households, at October to December 2026 prices and then at January to March 2027 prices. A
          proxy, not the official fuel poverty measure.
        </p>
      </div>
      <div className="metric-card" data-testid="tile-payment-covers">
        <p className="eyebrow text-slate-500">£100 payment covers the rise</p>
        <p className="text-3xl font-bold">{pct(summary.hep_covers_quarter_rise_pct)}</p>
        <p className="text-sm text-slate-600">
          Of households that receive the Household Energy Payment: the payment is at least the rise in their bill
          over January to March 2027 alone.
        </p>
      </div>
      <p className="text-sm text-slate-600 sm:col-span-2">
        A higher price does not change measured income poverty, which counts income, not spending. Support paid in
        cash does raise income.
      </p>
    </section>
  );
}
