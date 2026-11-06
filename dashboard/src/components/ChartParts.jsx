"use client";

import { ResponsiveContainer } from "recharts";
import { axisStyle } from "../utils/chartTheme";

/**
 * A chart's frame with a set initial size, so the prerender has a width
 * and height to draw at (no width(-1) warning) before the browser measures.
 */
export function ChartFrame({ height, children }) {
  return (
    <div style={{ width: "100%", height, minHeight: height }}>
      <ResponsiveContainer initialDimension={{ width: 800, height }}>{children}</ResponsiveContainer>
    </div>
  );
}

/** Split a label into lines of at most ``max`` characters, on spaces. */
export function wrapLabel(text, max) {
  const lines = [];
  let line = "";
  for (const word of String(text).split(" ")) {
    if (line && (line + " " + word).length > max) {
      lines.push(line);
      line = word;
    } else {
      line = line ? `${line} ${word}` : word;
    }
  }
  if (line) lines.push(line);
  return lines;
}

/** Y-axis width for category labels: wide enough, at most 40% of a phone. */
export function categoryAxisWidth(labels, narrow) {
  const longest = Math.max(0, ...labels.map((l) => String(l).length));
  if (narrow) return Math.min(140, Math.max(80, Math.min(longest, 18) * 7));
  return Math.min(280, Math.max(100, longest * 7));
}

/** A category tick that wraps onto lines that fit its axis width. */
export function WrappedTick({ x, y, payload, width = 140 }) {
  const lines = wrapLabel(payload.value, Math.max(8, Math.floor(width / 7)));
  const top = -((lines.length - 1) * 14) / 2;
  return (
    <text x={x} y={y} textAnchor="end" fontSize={axisStyle.fontSize} fill={axisStyle.fill}>
      {lines.map((line, i) => (
        <tspan key={i} x={x} dy={i === 0 ? top + 4 : 14}>
          {line}
        </tspan>
      ))}
    </text>
  );
}

/** Tooltip with formatted values (no raw numbers such as 143.67). */
export function ChartTooltip({ active, payload, label, format, labelFormat }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip" role="status">
      <p className="chart-tooltip-label">{labelFormat ? labelFormat(label, payload) : label}</p>
      {payload.map((item) => (
        <p key={item.dataKey}>
          {item.name}: <strong>{format(item.value, item)}</strong>
        </p>
      ))}
    </div>
  );
}
