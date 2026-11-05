// Chart colours in one place (docs/COLOURS.md). Components never write a
// hex value: they take it from here. Teal and grey only, as on other
// PolicyEngine dashboards. A rise in bills is grey, support is teal.
export const chartColours = {
  gain: "#2C7A7B", // primary-600: support, a fall in bills
  loss: "#9CA3AF", // gray-400: a rise in bills
  neutral: "#6B7280", // gray-500
  restated: "#D1D5DB", // gray-300: a level restated on another basis
  grid: "#E2E8F0", // border-light
  axis: "#4B5563", // gray-600
  series: ["#285E61", "#4FD1C5"], // primary-700, primary-300
};

export const axisStyle = { fontSize: 12, fill: chartColours.axis };

/** Colour for the n-th series in a chart (two at most). */
export function seriesColour(index) {
  const { series } = chartColours;
  if (index < 0 || index >= series.length) {
    throw new Error(`No colour assigned for series index ${index}`);
  }
  return series[index];
}
