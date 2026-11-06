"use client";

import { useRef } from "react";
import { toCsv } from "../utils/format";
import { downloadName } from "../utils/releaseMode";

function save(blob, name) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

/** The chart's own SVG, with its size fixed so it renders outside the page. */
export function chartSvgText(svg) {
  const copy = svg.cloneNode(true);
  const { width, height } = svg.getBoundingClientRect();
  copy.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  if (width && height) {
    copy.setAttribute("width", String(Math.round(width)));
    copy.setAttribute("height", String(Math.round(height)));
  }
  return new XMLSerializer().serializeToString(copy);
}

/**
 * Download the rows behind a chart as CSV, or the chart as SVG or PNG.
 * In a drill build every file name starts MOCK- (utils/releaseMode.js).
 */
export default function ChartDownloadMenu({ rows, filename, title }) {
  const ref = useRef(null);
  const label = title ?? filename;
  const findSvg = () => ref.current?.closest("section")?.querySelector("svg.recharts-surface") ?? null;

  const csv = () => save(new Blob([toCsv(rows)], { type: "text/csv" }), downloadName(`${filename}.csv`));
  const svg = () => {
    const node = findSvg();
    if (!node) return;
    save(new Blob([chartSvgText(node)], { type: "image/svg+xml" }), downloadName(`${filename}.svg`));
  };
  const png = () => {
    const node = findSvg();
    if (!node) return;
    const { width, height } = node.getBoundingClientRect();
    const image = new Image();
    image.onload = () => {
      const scale = 2;
      const canvas = document.createElement("canvas");
      canvas.width = Math.round(width * scale);
      canvas.height = Math.round(height * scale);
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(image, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => blob && save(blob, downloadName(`${filename}.png`)));
    };
    image.src = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(chartSvgText(node))}`;
  };

  return (
    <div ref={ref} className="flex flex-wrap gap-1" role="group" aria-label={`Download ${label}`}>
      <button type="button" className="toggle-button" onClick={csv} aria-label={`Download ${label} as CSV`}>
        CSV
      </button>
      <button type="button" className="toggle-button" onClick={png} aria-label={`Download ${label} as PNG`}>
        PNG
      </button>
      <button type="button" className="toggle-button" onClick={svg} aria-label={`Download ${label} as SVG`}>
        SVG
      </button>
    </div>
  );
}
