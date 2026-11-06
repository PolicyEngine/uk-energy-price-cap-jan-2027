// Readers for results.json cells (docs/RESULTS_SCHEMA.md). A cell is
// { value } or { withheld: true }; withheld reads as null.
export function cellValue(cell) {
  if (!cell || cell.withheld) return null;
  return cell.value;
}

export function scenarioById(cap, id) {
  return cap.scenarios.find((s) => s.id === id) ?? null;
}

/** Bill change by decile for one scenario. */
export function billDecileRows(bills, scenarioId) {
  return bills.by_decile
    .filter((r) => r.scenario_id === scenarioId)
    .map((r) => ({
      decile: r.decile,
      gross_change_gbp: cellValue(r.gross_change_gbp),
      change_after_support_gbp: cellValue(r.change_after_support_gbp),
      share_of_net_income_pct: cellValue(r.share_of_net_income_pct),
    }));
}

export function billGroupRows(bills, scenarioId, dimension) {
  return bills.by_group
    .filter((r) => r.scenario_id === scenarioId && r.dimension === dimension)
    .map((r) => ({
      group: r.group,
      gross_change_gbp: cellValue(r.gross_change_gbp),
      outside_cap: r.outside_cap,
    }));
}

/** Average gain by decile, summed over the selected support measures. */
export function supportDecileRows(cells, selectedIds) {
  const rows = [];
  for (let d = 1; d <= 10; d += 1) {
    const mine = cells.filter((c) => c.decile === d && selectedIds.includes(c.measure_id));
    const values = mine.map((c) => cellValue(c.avg_change_gbp));
    const withheld = values.some((v) => v === null);
    rows.push({
      decile: d,
      avg_change_gbp: withheld ? null : values.reduce((s, v) => s + v, 0),
      withheld,
    });
  }
  return rows;
}
