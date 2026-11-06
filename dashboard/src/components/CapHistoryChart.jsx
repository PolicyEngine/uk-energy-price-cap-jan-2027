"use client";

import { Bar, BarChart, CartesianGrid, Cell, Tooltip, XAxis, YAxis } from "recharts";
import { axisStyle, chartColours, seriesColour } from "../utils/chartTheme";
import { formatGbp, formatGbpTick } from "../utils/format";
import useNarrow from "../utils/useNarrow";
import ChartDownloadMenu from "./ChartDownloadMenu";
import ChartLogo from "./ChartLogo";
import { ChartFrame, ChartTooltip } from "./ChartParts";

const TITLE = "Typical Direct Debit dual-fuel bill (£ a year)";

/** "2026Q1" -> "Q1 26", for narrow screens. */
export function shortPeriod(period) {
  return `${period.slice(4)} ${period.slice(2, 4)}`;
}

/**
 * Cap history with its basis on every bar. A level on the old
 * typical-consumption basis is a lighter bar, so the July 2026 change of
 * basis never reads as a price change. The January to March 2027 bar is
 * outlined and labelled from the data: placeholder until Ofgem publishes.
 */
export function historyRows(cap, scenario) {
  const rows = cap.history.map((h) => ({
    period: h.period,
    label: h.tdcv_basis === "2023" ? `${h.label} (2023 basis)` : h.label,
    short: h.tdcv_basis === "2023" ? `${shortPeriod(h.period)}*` : shortPeriod(h.period),
    direct_debit: h.direct_debit,
    basis: h.tdcv_basis,
    restated: Boolean(h.restated),
    scenario: false,
  }));
  const status = scenario.placeholder ? "placeholder" : "announced";
  rows.push({
    period: "2027Q1",
    label: `Jan to Mar 2027 (${status})`,
    short: `${shortPeriod("2027Q1")} (${status})`,
    direct_debit: scenario.direct_debit,
    basis: "2026",
    restated: false,
    scenario: true,
  });
  return rows;
}

export default function CapHistoryChart({ cap, scenario }) {
  const narrow = useNarrow();
  const rows = historyRows(cap, scenario);
  return (
    <section className="panel" aria-label="Cap history">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-4">
        <h3 className="text-lg font-semibold">{TITLE}</h3>
        <ChartDownloadMenu rows={rows} filename="cap-history" title={TITLE} />
      </div>
      <ChartFrame height={narrow ? 260 : 300}>
        <BarChart data={rows} margin={{ left: 8, right: 8, bottom: 8 }}>
          <CartesianGrid stroke={chartColours.grid} vertical={false} />
          {narrow ? (
            <XAxis dataKey="short" tick={axisStyle} interval={0} height={40} />
          ) : (
            <XAxis dataKey="label" tick={axisStyle} interval={0} angle={-15} height={60} textAnchor="end" />
          )}
          <YAxis tick={axisStyle} tickFormatter={formatGbpTick} width={56} />
          <Tooltip
            content={
              <ChartTooltip
                format={(v) => formatGbp(v)}
                labelFormat={(_, payload) => payload?.[0]?.payload?.label ?? ""}
              />
            }
          />
          <Bar isAnimationActive={false} dataKey="direct_debit" name="Typical bill">
            {rows.map((r) => (
              <Cell
                key={r.label}
                fill={r.scenario ? chartColours.scenario : r.basis === "2023" ? chartColours.restated : seriesColour(0)}
                stroke={r.scenario ? seriesColour(0) : undefined}
                strokeDasharray={r.scenario ? "4 3" : undefined}
                strokeWidth={r.scenario ? 2 : 0}
              />
            ))}
          </Bar>
        </BarChart>
      </ChartFrame>
      <p className="mt-2 text-sm text-slate-600" data-testid="basis-note">
        From July 2026 Ofgem measures typical use as 2,500 kWh of electricity and 9,500 kWh of gas a year, down from
        2,700 and 11,500. Lighter bars{narrow ? " (marked *)" : ""} use the earlier basis. The July to September 2026
        level is £1,862 on the earlier basis and £1,663 on the new one: the same prices. The outlined bar is January to
        March 2027.
      </p>
      <ChartLogo />
    </section>
  );
}
