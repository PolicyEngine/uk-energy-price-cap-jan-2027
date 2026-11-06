"use client";

import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours } from "../utils/chartTheme";
import { billGroupRows } from "../utils/dataHelpers";
import { formatGbp, formatGbpTick } from "../utils/format";
import useNarrow from "../utils/useNarrow";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import { categoryAxisWidth, ChartFrame, ChartTooltip, WrappedTick } from "./ChartParts";

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
  NORTHERN_IRELAND: "Northern Ireland",
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

// ONS order: English regions, then Wales and Scotland; Northern Ireland,
// outside the cap, last.
const REGION_ORDER = [
  "NORTH_EAST",
  "NORTH_WEST",
  "YORKSHIRE",
  "EAST_MIDLANDS",
  "WEST_MIDLANDS",
  "EAST_OF_ENGLAND",
  "LONDON",
  "SOUTH_EAST",
  "SOUTH_WEST",
  "WALES",
  "SCOTLAND",
  "NORTHERN_IRELAND",
];

/** Readable name for a group code; council tax bands read as "Band A". */
export function groupLabel(dimension, group) {
  if (dimension === "council_tax_band") return group === "I" ? "Band I (Wales only)" : `Band ${group}`;
  return GROUP_LABELS[group] ?? group;
}

/** Rows in reading order: regions in ONS order, other groups as given. */
export function orderGroups(dimension, rows) {
  if (dimension !== "region") return rows;
  const rank = (g) => (REGION_ORDER.indexOf(g) === -1 ? REGION_ORDER.length : REGION_ORDER.indexOf(g));
  return [...rows].sort((a, b) => rank(a.group) - rank(b.group));
}

/** Change in energy spend by household group (one dimension at a time). */
export default function GroupChart({ bills, scenarioId }) {
  const [dimension, setDimension] = useState("region");
  const narrow = useNarrow();
  const rows = orderGroups(dimension, billGroupRows(bills, scenarioId, dimension)).map((r) => ({
    ...r,
    label: groupLabel(dimension, r.group),
  }));
  const axisWidth = categoryAxisWidth(
    rows.map((r) => r.label),
    narrow,
  );
  const title = `Average change in household energy spend by ${DIMENSIONS[dimension].toLowerCase()} (£ a year)`;
  return (
    <section className="panel" aria-label="Change in energy spend by group">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">{title}</h3>
        <ChartDownloadMenu rows={rows} filename={`bill-change-${dimension}-${scenarioId}`} title={title} />
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
      <ChartFrame height={Math.max(240, (narrow ? 40 : 32) * rows.length)}>
        <BarChart data={rows} layout="vertical" margin={{ left: 8, right: 16 }}>
          <CartesianGrid stroke={chartColours.grid} horizontal={false} />
          <XAxis type="number" tick={axisStyle} tickFormatter={formatGbpTick} />
          <YAxis
            type="category"
            dataKey="label"
            width={axisWidth}
            interval={0}
            tick={<WrappedTick width={axisWidth} />}
          />
          <Tooltip content={<ChartTooltip format={(v) => formatGbp(v, { sign: true })} />} />
          <Bar isAnimationActive={false} dataKey="gross_change_gbp" name="Change, £ a year" fill={chartColours.loss} />
        </BarChart>
      </ChartFrame>
      {rows.some((r) => r.outside_cap) && (
        <p className="mt-2 text-sm text-slate-600">
          Northern Ireland is outside the Ofgem cap and is not moved by it. It has domestic rates, not council tax
          bands, so it is left out of the band breakdown.
        </p>
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
