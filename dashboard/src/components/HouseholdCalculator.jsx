"use client";

import { formatGbpPence } from "../utils/format";
import useNarrow from "../utils/useNarrow";

function rowsFor(households, scenarioId) {
  return households.map((h) => {
    const then = h.bill_jan_mar_2027[scenarioId];
    const change = Math.round((then - h.bill_oct_dec_2026) * 100) / 100;
    return { h, then, change, after: Math.round((change - h.support.total) * 100) / 100 };
  });
}

/**
 * Example households: annual bill now and in January to March 2027, and the
 * support each receives under current law. Bills come from Ofgem rates and
 * kWh (src/uk_energy_price_cap/household.py), so this tab runs with no model.
 * Below 640 px each household is a card, so no column sits off-screen.
 */
export default function HouseholdCalculator({ households, scenarioId, placeholder }) {
  const narrow = useNarrow();
  const rows = rowsFor(households, scenarioId);
  return (
    <section className="panel" aria-label="Household examples">
      <h3 className="mb-2 text-lg font-semibold">Example households (£ a year)</h3>
      {placeholder && (
        <p className="mb-3 text-sm text-slate-600" data-testid="household-scaling-note">
          January to March 2027 bills scale today&apos;s rates by one ratio until Ofgem publishes its rates by fuel and
          payment method.
        </p>
      )}
      {narrow ? (
        <div className="household-cards" data-testid="household-cards">
          {rows.map(({ h, then, change, after }) => (
            <article key={h.id} className="household-card panel">
              <h4 className="mb-1 font-semibold">{h.label}</h4>
              <dl>
                <dt>Bill at Oct to Dec 2026 rates</dt>
                <dd>{formatGbpPence(h.bill_oct_dec_2026)}</dd>
                <dt>Bill at Jan to Mar 2027 rates</dt>
                <dd>{formatGbpPence(then)}</dd>
                <dt>Change</dt>
                <dd>{formatGbpPence(change, { sign: true })}</dd>
                <dt>Support</dt>
                <dd>{formatGbpPence(h.support.total)}</dd>
                <dt>Change after support</dt>
                <dd>{formatGbpPence(after, { sign: true })}</dd>
              </dl>
            </article>
          ))}
        </div>
      ) : (
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
              {rows.map(({ h, then, change, after }) => (
                <tr key={h.id}>
                  <td>{h.label}</td>
                  <td>
                    {h.inputs.electricity_kwh.toLocaleString("en-GB")} / {h.inputs.gas_kwh.toLocaleString("en-GB")}
                  </td>
                  <td>{formatGbpPence(h.bill_oct_dec_2026)}</td>
                  <td>{formatGbpPence(then)}</td>
                  <td>{formatGbpPence(change, { sign: true })}</td>
                  <td>{formatGbpPence(h.support.total)}</td>
                  <td>{formatGbpPence(after, { sign: true })}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="mt-2 text-sm text-slate-600">
        Bills are to the penny from Ofgem&apos;s GB average unit rates and standing charges, so the typical household
        can differ by under £1 from Ofgem&apos;s headline level, which Ofgem rounds to the pound. Support: the £100
        Household Energy Payment (England, council tax bands A to D); the £150 Warm Home Discount (England and Wales,
        qualifying benefits; Scotland, Pension Credit Guarantee Credit); the Winter Fuel Payment (England and Wales)
        or the Pension Age Winter Heating Payment (Scotland), for households with someone over State Pension age,
        before any recovery through income tax.
      </p>
    </section>
  );
}
