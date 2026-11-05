"use client";

import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, seriesColour } from "../utils/chartTheme";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

/**
 * Cap history with its basis on every bar. A level restated on the old
 * typical-consumption basis is a lighter bar, so the July 2026 change of
 * basis never reads as a price change.
 */
export function historyRows(cap, scenario) {
  const rows = cap.history.map((h) => ({
    label: h.tdcv_basis === "2023" ? `${h.label} (2023 basis)` : h.label,
    direct_debit: h.direct_debit,
    basis: h.tdcv_basis,
    restated: Boolean(h.restated),
  }));
  rows.push({ label: "Jan to Mar 2027 (placeholder)", direct_debit: scenario.direct_debit, basis: "2026", restated: false });
  return rows;
}

export default function CapHistoryChart({ cap, scenario }) {
  const rows = historyRows(cap, scenario);
  return (
    <section className="panel" aria-label="Cap history">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Typical Direct Debit dual-fuel bill (£ a year)</h3>
        <ChartDownloadMenu rows={rows} filename="cap-history" />
      </div>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <BarChart data={rows} margin={{ left: 40, right: 16, bottom: 8 }}>
            <CartesianGrid stroke={chartColours.grid} vertical={false} />
            <XAxis dataKey="label" tick={axisStyle} interval={0} angle={-15} height={60} textAnchor="end" />
            <YAxis tick={axisStyle} />
            <Tooltip />
            <Bar isAnimationActive={false} dataKey="direct_debit" name="£ a year">
              {rows.map((r) => (
                <Cell
                  key={r.label}
                  fill={r.basis === "2023" ? chartColours.restated : seriesColour(0)}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-sm text-slate-600" data-testid="basis-note">
        From July 2026 Ofgem measures typical use as 2,500 kWh of electricity and 9,500 kWh of gas, down from 2,700 and
        11,500. Lighter bars use the earlier basis. The July to September 2026 level is £1,862 on the earlier basis and
        £1,663 on the new one: the same prices.
      </p>
      <ChartLogo />
    </section>
  );
}
