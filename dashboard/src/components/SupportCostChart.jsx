"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { formatMillions } from "../utils/format";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

/** Exchequer cost of each selected support measure (£ million, in its policy year). */
export default function SupportCostChart({ measures, years }) {
  const label = (y) => years.find((x) => x.year === y)?.label ?? String(y);
  const rows = measures.map((m) => ({
    measure: m.name,
    year: label(m.year),
    cost_gbp_m: m.cost_gbp_m,
    households_reached_m: m.households_reached_m,
  }));
  return (
    <section className="panel" aria-label="Cost of support measures">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Cost of each measure (£ million)</h3>
        <ChartDownloadMenu rows={rows} filename="support-cost" />
      </div>
      <div style={{ width: "100%", height: Math.max(200, 44 * rows.length) }}>
        <ResponsiveContainer>
          <BarChart data={rows} layout="vertical" margin={{ left: 24, right: 24 }}>
            <CartesianGrid stroke={chartColours.grid} horizontal={false} />
            <XAxis type="number" tick={axisStyle} />
            <YAxis type="category" dataKey="measure" width={280} tick={axisStyle} />
            <Tooltip formatter={(v) => formatMillions(v)} />
            <Bar isAnimationActive={false} dataKey="cost_gbp_m" name="Cost" fill={chartColours.gain} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <table className="data-table compact mt-3">
        <thead>
          <tr>
            <th>Measure</th>
            <th>Year</th>
            <th>Cost</th>
            <th>Households reached</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.measure}>
              <td>{r.measure}</td>
              <td>{r.year}</td>
              <td>{formatMillions(r.cost_gbp_m)}</td>
              <td>{r.households_reached_m === null ? "–" : `${r.households_reached_m.toFixed(1)}m`}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <ChartLogo />
    </section>
  );
}
