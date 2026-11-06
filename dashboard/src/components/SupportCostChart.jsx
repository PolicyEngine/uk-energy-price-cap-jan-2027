"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { formatMillions } from "../utils/format";
import useNarrow from "../utils/useNarrow";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import { categoryAxisWidth, ChartFrame, ChartTooltip, WrappedTick } from "./ChartParts";

const TITLE = "Cost of each measure (£ million, in its fiscal year)";

/** Exchequer cost of each selected support measure (£ million, in its policy year). */
export default function SupportCostChart({ measures, years }) {
  const narrow = useNarrow();
  const [table, setTable] = useState(false);
  const label = (y) => years.find((x) => x.year === y)?.label ?? String(y);
  const rows = measures.map((m) => ({
    measure: `${m.name} (${label(m.year)})`,
    year: label(m.year),
    cost_gbp_m: m.cost_gbp_m,
    households_reached_m: m.households_reached_m,
  }));
  const axisWidth = categoryAxisWidth(
    rows.map((r) => r.measure),
    narrow,
  );
  return (
    <section className="panel" aria-label="Cost of support measures">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">{TITLE}</h3>
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className={`toggle-button${table ? " active" : ""}`}
            aria-pressed={table}
            onClick={() => setTable(!table)}
          >
            {table ? "Show chart" : "Show table"}
          </button>
          <ChartDownloadMenu rows={rows} filename="support-cost" title={TITLE} />
        </div>
      </div>
      {table ? (
        <table className="data-table compact" data-testid="support-cost-table">
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
      ) : (
        <ChartFrame height={Math.max(200, (narrow ? 64 : 48) * rows.length)}>
          <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
            <CartesianGrid stroke={chartColours.grid} horizontal={false} />
            <XAxis type="number" tick={axisStyle} tickFormatter={(v) => formatMillions(v)} />
            <YAxis
              type="category"
              dataKey="measure"
              width={axisWidth}
              interval={0}
              tick={<WrappedTick width={axisWidth} />}
            />
            <Tooltip content={<ChartTooltip format={(v) => formatMillions(v)} />} />
            <Bar isAnimationActive={false} dataKey="cost_gbp_m" name="Cost" fill={chartColours.gain} />
          </BarChart>
        </ChartFrame>
      )}
      <ChartLogo />
    </section>
  );
}
