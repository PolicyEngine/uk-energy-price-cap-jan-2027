"use client";

import { toCsv } from "../utils/format";

/** Download the rows behind a chart as CSV (scaled down: CSV only). */
export default function ChartDownloadMenu({ rows, filename }) {
  const onClick = () => {
    const blob = new Blob([toCsv(rows)], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <button type="button" className="toggle-button" onClick={onClick}>
      Download CSV
    </button>
  );
}
