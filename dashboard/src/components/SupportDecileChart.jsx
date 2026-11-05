"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { supportDecileRows } from "../utils/dataHelpers";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

/** Average gain from the selected support measures by income decile. */
export default function SupportDecileChart({ cells, selectedIds }) {
  const rows = supportDecileRows(cells, selectedIds);
  return (
    <section className="panel" aria-label="Gain from support by income decile">
      <div className="mb-3 flex items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Average gain from the selected measures by income decile (£ a year)</h3>
        <ChartDownloadMenu rows={rows} filename="support-deciles" />
      </div>
      <div style={{ width: "100%", height: 300 }}>
        <ResponsiveContainer>
          <BarChart data={rows}>
            <CartesianGrid stroke={chartColours.grid} vertical={false} />
            <XAxis dataKey="decile" tick={axisStyle} />
            <YAxis tick={axisStyle} />
            <Tooltip />
            <Bar isAnimationActive={false} dataKey="avg_change_gbp" name="£ a year" fill={chartColours.gain} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {rows.some((r) => r.withheld) && (
        <p className="mt-2 text-sm text-slate-600" data-testid="withheld-note">
          Deciles with no bar rest on fewer than 10 survey households for at least one selected measure.
        </p>
      )}
      <ChartLogo />
    </section>
  );
}
