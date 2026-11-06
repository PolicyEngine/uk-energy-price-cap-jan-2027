// Which measures each part of the page shows, read from results.json (the
// registry), never from a hard-coded list (Autumn Budget repo, #60, #144).

/** Support measures with figures: the chips, cost chart and decile chart. */
export function chartedMeasures(measures) {
  return measures.filter((m) => m.computable && m.lever === "support" && !m.calculator_only);
}

/** Measures shown only in the household calculator. */
export function calculatorOnlyMeasures(measures) {
  return measures.filter((m) => m.calculator_only);
}

/** Measures with no figures, with the reason (shown as not computable, never £0). */
export function notComputableMeasures(measures) {
  return measures.filter((m) => !m.computable);
}
