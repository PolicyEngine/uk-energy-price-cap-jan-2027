"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, seriesColour } from "../utils/chartTheme";
import { billDecileRows } from "../utils/dataHelpers";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

/** Change in household energy spend by income decile, gross and after support. */
export default function BillChangeChart({ bills, scenarioId }) {
  const [unit, setUnit] = useState("gbp");
  const rows = billDecileRows(bills, scenarioId);
  return (
    <section className="panel" aria-label="Change in energy spend by income decile">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">
          {unit === "gbp"
            ? "Average change in household energy spend by income decile (£ a year)"
            : "Average change in energy spend as a share of net income, by income decile (%)"}
        </h3>
        <div className="flex gap-2">
          <button type="button" className={`toggle-button${unit === "gbp" ? " active" : ""}`} onClick={() => setUnit("gbp")}>
            £ a year
          </button>
          <button type="button" className={`toggle-button${unit === "pct" ? " active" : ""}`} onClick={() => setUnit("pct")}>
            % of income
          </button>
          <ChartDownloadMenu rows={rows} filename={`bill-change-deciles-${scenarioId}`} />
        </div>
      </div>
      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <BarChart data={rows}>
            <CartesianGrid stroke={chartColours.grid} vertical={false} />
            <XAxis dataKey="decile" tick={axisStyle} />
            <YAxis tick={axisStyle} />
            <Tooltip />
            <Legend />
            {unit === "gbp" ? (
              <>
                <Bar isAnimationActive={false} dataKey="gross_change_gbp" name="Before support" fill={chartColours.loss} />
                <Bar isAnimationActive={false} dataKey="change_after_support_gbp" name="After current support" fill={seriesColour(0)} />
              </>
            ) : (
              <Bar isAnimationActive={false} dataKey="share_of_net_income_pct" name="Share of net income" fill={chartColours.loss} />
            )}
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-sm text-slate-600">
        Decile 1 holds the tenth of households with the lowest net income. Changes are annualised at January to March
        2027 prices. Current support is the Household Energy Payment, the Warm Home Discount and the Winter Fuel
        Payment.
      </p>
      <ChartLogo />
    </section>
  );
}
