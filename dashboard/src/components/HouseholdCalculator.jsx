"use client";

import { formatGbp } from "../utils/format";

/**
 * Example households: annual bill now and in January to March 2027, and the
 * support each receives under current law. Bills come from Ofgem rates and
 * kWh (src/uk_energy_price_cap/household.py), so this tab runs with no model.
 */
export default function HouseholdCalculator({ households, scenarioId, placeholder }) {
  return (
    <section className="panel" aria-label="Household examples">
      <h3 className="mb-2 text-lg font-semibold">Example households (£ a year)</h3>
      {placeholder && (
        <p className="mb-3 text-sm text-slate-600">
          Placeholder: January to March 2027 bills use one scaling of today&apos;s rates. On the day they use
          Ofgem&apos;s rates by fuel and payment method.
        </p>
      )}
      <div className="overflow-x-auto">
        <table className="data-table" data-testid="household-table">
          <thead>
            <tr>
              <th>Household</th>
              <th>kWh (electricity / gas)</th>
              <th>Bill, Oct to Dec 2026 rates</th>
              <th>Bill, Jan to Mar 2027 rates</th>
              <th>Change</th>
              <th>Support</th>
              <th>Change after support</th>
            </tr>
          </thead>
          <tbody>
            {households.map((h) => {
              const then = h.bill_jan_mar_2027[scenarioId];
              const change = then - h.bill_oct_dec_2026;
              return (
                <tr key={h.id}>
                  <td>{h.label}</td>
                  <td>
                    {h.inputs.electricity_kwh.toLocaleString("en-GB")} / {h.inputs.gas_kwh.toLocaleString("en-GB")}
                  </td>
                  <td>{formatGbp(h.bill_oct_dec_2026)}</td>
                  <td>{formatGbp(then)}</td>
                  <td>{formatGbp(change, { sign: true })}</td>
                  <td>{formatGbp(h.support.total)}</td>
                  <td>{formatGbp(change - h.support.total, { sign: true })}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-sm text-slate-600">
        Support: the £100 Household Energy Payment (England, council tax bands A to D), the £150 Warm Home Discount
        (England and Wales, qualifying benefits) and the Winter Fuel Payment (households with someone over State Pension
        age, before any recovery through income tax).
      </p>
    </section>
  );
}
