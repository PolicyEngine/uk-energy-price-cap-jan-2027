import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import results from "../../public/data/results.json";
import Dashboard, { VIEWS } from "./Dashboard";

beforeEach(() => window.history.replaceState(null, "", "/"));
afterEach(cleanup);

describe("Dashboard", () => {
  it("shows the placeholder notice from results.json", () => {
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("placeholder-note").textContent).toMatch(/placeholder/i);
  });

  it("opens on the cap with one chip per scenario", () => {
    render(<Dashboard data={results} />);
    expect(screen.getAllByTestId("scenario-chip")).toHaveLength(results.cap.scenarios.length);
    expect(screen.getByTestId("tile-cap").textContent).toContain("£2,180");
    expect(screen.getByTestId("basis-note").textContent).toMatch(/2,500 kWh/);
  });

  it("writes the scenario to the address", () => {
    render(<Dashboard data={results} />);
    fireEvent.click(screen.getAllByTestId("scenario-chip")[0]);
    expect(window.location.search).toContain(`scenario=${results.cap.scenarios[0].id}`);
  });

  it("offers one chip per computable support measure, read from the catalogue", () => {
    window.history.replaceState(null, "", "/?tab=support");
    render(<Dashboard data={results} />);
    const expected = results.measures.filter((m) => m.computable && m.lever === "support");
    expect(screen.getAllByTestId("policy-chip")).toHaveLength(expected.length);
    const names = screen.getAllByTestId("policy-chip").map((c) => c.textContent);
    for (const m of results.measures.filter((x) => !x.computable)) expect(names).not.toContain(m.name);
  });

  it("lists every measure on the Policies tab, with reasons for the rest", () => {
    render(<Dashboard data={results} />);
    expect(screen.getAllByRole("tab").length).toBeGreaterThanOrEqual(VIEWS.length);
    fireEvent.click(screen.getByRole("tab", { name: "Policies" }));
    expect(window.location.search).toContain("tab=policies");
    expect(screen.getAllByTestId("policy-card")).toHaveLength(results.measures.length);
    expect(screen.getAllByTestId("limit-reason")).toHaveLength(results.measures.filter((m) => !m.computable).length);
  });

  it("labels the run as unvalidated on the Methodology tab", () => {
    window.history.replaceState(null, "", "/?tab=methodology");
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("replication").textContent).toMatch(/unvalidated under this engine/i);
  });

  it("lists every household preset", () => {
    window.history.replaceState(null, "", "/?tab=household");
    render(<Dashboard data={results} />);
    const rows = screen.getByTestId("household-table").querySelectorAll("tbody tr");
    expect(rows).toHaveLength(results.households.length);
  });

  it("shows withheld groups as withheld", () => {
    window.history.replaceState(null, "", "/?tab=bills&sub=groups");
    render(<Dashboard data={results} />);
    fireEvent.click(screen.getByRole("button", { name: "Council tax band" }));
    expect(screen.getByTestId("withheld-note")).toBeTruthy();
  });
});
