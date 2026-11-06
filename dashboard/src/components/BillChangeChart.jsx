"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, seriesColour } from "../utils/chartTheme";
import { billDecileRows } from "../utils/dataHelpers";
import { formatGbp, formatGbpTick, formatPct, formatPctTick } from "../utils/format";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import { ChartFrame, ChartTooltip } from "./ChartParts";

const LEGEND_ORDER = ["gross_change_gbp", "change_after_support_gbp", "share_of_net_income_pct"];

/** Change in household energy spend by income decile, gross and after support. */
export default function BillChangeChart({ bills, scenarioId }) {
  const [unit, setUnit] = useState("gbp");
  const rows = billDecileRows(bills, scenarioId);
  const title =
    unit === "gbp"
      ? "Average change in household energy spend by income decile (£ a year)"
      : "Average change in energy spend as a share of net income, by income decile (%)";
  const format = unit === "gbp" ? (v) => formatGbp(v, { sign: true }) : (v) => formatPct(v);
  return (
    <section className="panel" aria-label="Change in energy spend by income decile">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="flex flex-wrap gap-2">
          <div className="flex gap-2" role="group" aria-label="Unit for the decile chart">
            <button
              type="button"
              aria-pressed={unit === "gbp"}
              className={`toggle-button${unit === "gbp" ? " active" : ""}`}
              onClick={() => setUnit("gbp")}
            >
              £ a year
            </button>
            <button
              type="button"
              aria-pressed={unit === "pct"}
              className={`toggle-button${unit === "pct" ? " active" : ""}`}
              onClick={() => setUnit("pct")}
            >
              % of income
            </button>
          </div>
          <ChartDownloadMenu rows={rows} filename={`bill-change-deciles-${scenarioId}`} title={title} />
        </div>
      </div>
      <ChartFrame height={320}>
        <BarChart data={rows}>
          <CartesianGrid stroke={chartColours.grid} vertical={false} />
          <XAxis dataKey="decile" tick={axisStyle} />
          <YAxis tick={axisStyle} tickFormatter={unit === "gbp" ? formatGbpTick : formatPctTick} />
          <Tooltip content={<ChartTooltip format={format} labelFormat={(d) => `Decile ${d}`} />} />
          <Legend itemSorter={(item) => LEGEND_ORDER.indexOf(item.dataKey)} />
          {unit === "gbp" ? (
            <>
              <Bar isAnimationActive={false} dataKey="gross_change_gbp" name="Before support" fill={chartColours.loss} />
              <Bar
                isAnimationActive={false}
                dataKey="change_after_support_gbp"
                name="After current support"
                fill={seriesColour(0)}
              />
            </>
          ) : (
            <Bar isAnimationActive={false} dataKey="share_of_net_income_pct" name="Share of net income" fill={chartColours.loss} />
          )}
        </BarChart>
      </ChartFrame>
      <p className="mt-2 text-sm text-slate-600">
        Decile 1 holds the tenth of households with the lowest net income. Current support is the Household Energy
        Payment, the Warm Home Discount and the Winter Fuel Payment (in Scotland, the Pension Age Winter Heating
        Payment). The basis is on the <a href="?tab=methodology">Methodology</a> tab.
      </p>
      <ChartLogo />
    </section>
  );
}
