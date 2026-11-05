import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import results from "../../public/data/results.json";
import { historyRows } from "../components/CapHistoryChart";
import { calculatorOnlyMeasures, chartedMeasures, notComputableMeasures } from "./calculatorOnlyMeasures";
import { seriesColour } from "./chartTheme";
import { cellValue, supportDecileRows } from "./dataHelpers";
import { formatGbp, formatMillions, formatPct, toCsv } from "./format";
import { policyDetail } from "./policyDetails";

describe("utils", () => {
  it("policy text is ignored once the description changes", () => {
    const details = { a: { writtenFor: "old", summary: "text" } };
    expect(policyDetail({ id: "a", description: "old" }, details)).toBe("text");
    expect(policyDetail({ id: "a", description: "new" }, details)).toBeNull();
  });

  it("measure lists come from the catalogue", () => {
    const ms = [
      { id: "a", computable: true, lever: "support", calculator_only: false },
      { id: "b", computable: false, lever: "support", calculator_only: false },
      { id: "c", computable: true, lever: "bills", calculator_only: false },
      { id: "d", computable: true, lever: "support", calculator_only: true },
    ];
    expect(chartedMeasures(ms).map((m) => m.id)).toEqual(["a"]);
    expect(notComputableMeasures(ms).map((m) => m.id)).toEqual(["b"]);
    expect(calculatorOnlyMeasures(ms).map((m) => m.id)).toEqual(["d"]);
  });

  it("a withheld cell withholds its decile", () => {
    const cells = [
      { measure_id: "a", decile: 1, avg_change_gbp: { value: 5 } },
      { measure_id: "b", decile: 1, avg_change_gbp: { withheld: true } },
    ];
    expect(cellValue({ withheld: true })).toBeNull();
    expect(supportDecileRows(cells, ["a"])[0].avg_change_gbp).toBe(5);
    expect(supportDecileRows(cells, ["a", "b"])[0].avg_change_gbp).toBeNull();
  });

  it("cap history marks the old basis on every row that uses it", () => {
    const rows = historyRows(results.cap, results.cap.scenarios[0]);
    for (const r of rows.filter((x) => x.basis === "2023")) expect(r.label).toContain("2023 basis");
    expect(rows.at(-1).label).toMatch(/placeholder/);
  });

  it("formats and exports", () => {
    expect(formatGbp(-12.4)).toBe("−£12");
    expect(formatGbp(5, { sign: true })).toBe("+£5");
    expect(formatGbp(null)).toBe("withheld");
    expect(formatMillions(1889)).toBe("£1.9bn");
    expect(formatMillions(null)).toBe("not computable");
    expect(formatPct(26.5)).toBe("+26.5%");
    expect(toCsv([{ a: 1, b: "x,y" }])).toBe('a,b\n1,"x,y"');
    expect(() => seriesColour(5)).toThrow();
  });

  it("components take colours from chartTheme, never a hex literal", () => {
    const dir = resolve(__dirname, "../components");
    for (const file of readdirSync(dir).filter((f) => f.endsWith(".jsx") && !f.includes(".test."))) {
      const source = readFileSync(resolve(dir, file), "utf8").replace(/var\([^)]*\)/g, "");
      expect(source, file).not.toMatch(/#[0-9a-fA-F]{6}\b/);
    }
  });
});
