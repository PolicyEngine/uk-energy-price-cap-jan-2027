"use client";

import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { supportDecileRows } from "../utils/dataHelpers";
import { formatGbp, formatGbpTick } from "../utils/format";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import { ChartFrame, ChartTooltip } from "./ChartParts";

/** Average gain from the selected support measures by income decile, for one year. */
export default function SupportDecileChart({ cells, selectedIds, yearLabel }) {
  const rows = supportDecileRows(cells, selectedIds);
  const title = `Average gain from the selected measures by income decile, ${yearLabel} (£ a year)`;
  return (
    <section className="panel" aria-label="Gain from support by income decile">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <ChartDownloadMenu rows={rows} filename="support-deciles" title={title} />
      </div>
      <ChartFrame height={300}>
        <BarChart data={rows}>
          <CartesianGrid stroke={chartColours.grid} vertical={false} />
          <XAxis dataKey="decile" tick={axisStyle} />
          <YAxis tick={axisStyle} tickFormatter={formatGbpTick} />
          <Tooltip
            content={<ChartTooltip format={(v) => formatGbp(v, { sign: true })} labelFormat={(d) => `Decile ${d}`} />}
          />
          <Bar isAnimationActive={false} dataKey="avg_change_gbp" name="Gain, £ a year" fill={chartColours.gain} />
        </BarChart>
      </ChartFrame>
      <p className="mt-2 text-sm text-slate-600">
        Decile 1 holds the tenth of households with the lowest net income. Gains from several selected measures add
        up as if all were introduced together.
      </p>
      {rows.some((r) => r.withheld) && (
        <p className="mt-2 text-sm text-slate-600" data-testid="withheld-note">
          Deciles with no bar rest on fewer than 10 survey households for at least one selected measure.
        </p>
      )}
      <ChartLogo />
    </section>
  );
}
