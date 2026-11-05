"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { billGroupRows } from "../utils/dataHelpers";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";

export const DIMENSIONS = {
  region: "Region",
  tenure: "Tenure",
  council_tax_band: "Council tax band",
  fuel: "Gas or electric only",
  payment: "Prepayment",
};

const GROUP_LABELS = {
  NORTH_EAST: "North East",
  NORTH_WEST: "North West",
  YORKSHIRE: "Yorkshire and the Humber",
  EAST_MIDLANDS: "East Midlands",
  WEST_MIDLANDS: "West Midlands",
  EAST_OF_ENGLAND: "East of England",
  LONDON: "London",
  SOUTH_EAST: "South East",
  SOUTH_WEST: "South West",
  WALES: "Wales",
  SCOTLAND: "Scotland",
  NORTHERN_IRELAND: "Northern Ireland (outside the cap)",
  OWNED_OUTRIGHT: "Owned outright",
  OWNED_WITH_MORTGAGE: "Owned with a mortgage",
  RENT_FROM_COUNCIL: "Social rent (council)",
  RENT_FROM_HA: "Social rent (housing association)",
  RENT_PRIVATELY: "Private rent",
  dual_fuel: "Gas and electricity",
  electric_only: "Electricity only",
  prepayment: "Prepayment meter",
  other: "Other payment methods",
};

/** Readable name for a group code; council tax bands read as "Band A". */
export function groupLabel(dimension, group) {
  if (dimension === "council_tax_band") return `Band ${group}`;
  return GROUP_LABELS[group] ?? group;
}

/** Change in energy spend by household group (one dimension at a time). */
export default function GroupChart({ bills, scenarioId }) {
  const [dimension, setDimension] = useState("region");
  const rows = billGroupRows(bills, scenarioId, dimension).map((r) => ({ ...r, label: groupLabel(dimension, r.group) }));
  return (
    <section className="panel" aria-label="Change in energy spend by group">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">Average change in household energy spend by {DIMENSIONS[dimension].toLowerCase()} (£ a year)</h3>
        <ChartDownloadMenu rows={rows} filename={`bill-change-${dimension}-${scenarioId}`} />
      </div>
      <div className="mb-3 flex flex-wrap gap-2" role="group" aria-label="Group by">
        {Object.entries(DIMENSIONS).map(([k, label]) => (
          <button
            key={k}
            type="button"
            aria-pressed={dimension === k}
            className={`toggle-button${dimension === k ? " active" : ""}`}
            onClick={() => setDimension(k)}
          >
            {label}
          </button>
        ))}
      </div>
      <div style={{ width: "100%", height: Math.max(240, 32 * rows.length) }}>
        <ResponsiveContainer>
          <BarChart data={rows} layout="vertical" margin={{ left: 24, right: 24 }}>
            <CartesianGrid stroke={chartColours.grid} horizontal={false} />
            <XAxis type="number" tick={axisStyle} />
            <YAxis type="category" dataKey="label" width={240} tick={axisStyle} />
            <Tooltip />
            <Bar isAnimationActive={false} dataKey="gross_change_gbp" name="£ a year" fill={chartColours.loss} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      {rows.some((r) => r.outside_cap) && (
        <p className="mt-2 text-sm text-slate-600">Northern Ireland is outside the Ofgem cap and is not moved by it.</p>
      )}
      {rows.some((r) => r.gross_change_gbp === null) && (
        <p className="mt-2 text-sm text-slate-600" data-testid="withheld-note">
          Groups with no bar rest on fewer than 10 survey households and are withheld.
        </p>
      )}
      <ChartLogo />
    </section>
  );
}
