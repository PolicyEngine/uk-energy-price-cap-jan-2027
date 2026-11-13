import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import results from "../../public/data/results.json";
import Dashboard, { VIEWS } from "./Dashboard";

beforeEach(() => window.history.replaceState(null, "", "/"));
afterEach(cleanup);

describe("Dashboard", () => {
  it("leaves the placeholder notice to the banner (one home)", () => {
    render(<Dashboard data={results} />);
    expect(results.meta.placeholder).toBe(true);
    expect(screen.queryByTestId("run-note")).toBeNull();
  });

  it("shows the run's notice once figures are not placeholders", () => {
    const live = { ...results, meta: { ...results.meta, placeholder: false, notice: "Figures unvalidated" } };
    render(<Dashboard data={live} />);
    expect(screen.getByTestId("run-note").textContent).toBe("Figures unvalidated");
  });

  it("headline tiles read the scenario's summary", () => {
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("tile-total").textContent).toMatch(/£\d+\.\dbn/);
    expect(screen.getByTestId("tile-change").textContent).toMatch(/on October to December 2026/);
    expect(screen.getByTestId("tile-change").textContent).not.toMatch(/a year$/);
  });

  it("arrow keys move between tabs", () => {
    render(<Dashboard data={results} />);
    const first = screen.getByRole("tab", { name: "The cap" });
    fireEvent.keyDown(first, { key: "ArrowRight" });
    expect(window.location.search).toContain("tab=bills");
    fireEvent.keyDown(screen.getByRole("tab", { name: "Household bills" }), { key: "End" });
    expect(window.location.search).toContain("tab=methodology");
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
    // One measure selected by default, never measures from two years.
    const pressed = screen.getAllByTestId("policy-chip").filter((c) => c.getAttribute("aria-pressed") === "true");
    expect(pressed).toHaveLength(1);
    const other = expected.find((m) => m.year !== expected[0].year);
    fireEvent.click(screen.getByRole("button", { name: other.name }));
    const now = screen.getAllByTestId("policy-chip").filter((c) => c.getAttribute("aria-pressed") === "true");
    expect(now.map((c) => c.textContent)).toEqual([other.name]);
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
    // Plain reasons, with the issue as a link, not "(issue #N)" in the text.
    for (const r of screen.getAllByTestId("limit-reason")) expect(r.textContent).not.toMatch(/issue #/);
    expect(screen.getAllByTestId("policy-card")[0].textContent).toMatch(/Placeholder/);
  });

  it("shows a revenue-neutral bills measure by who pays less, not as a £0 cost", () => {
    render(<Dashboard data={results} />);
    fireEvent.click(screen.getByRole("tab", { name: "Policies" }));
    const gas = results.measures.find((m) => m.id === "gas_standing_charge_removal");
    expect(gas.computable && gas.lever === "bills").toBe(true);
    const card = document.getElementById("measure-gas_standing_charge_removal");
    expect(card.querySelector('[data-testid="bills-reach"]').textContent).toMatch(/Households paying less: [\d.]+m/);
    expect(card.textContent).not.toMatch(/Cost:/);
  });

  it("labels the run with its build and engine on the Methodology tab, with sources and plain basis labels", () => {
    window.history.replaceState(null, "", "/?tab=methodology");
    const label =
      "build uk-frs-calibration-attempt-20261112T133744Z-6f918b81, policyengine-uk 2.177.7, not in a policyengine.py release";
    const { unmount } = render(
      <Dashboard data={{ ...results, meta: { ...results.meta, engine: { ...results.meta.engine, label } } }} />,
    );
    expect(screen.getByTestId("replication").textContent).toContain(`Engine and data: ${label}.`);
    unmount();
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("replication").textContent).toMatch(/Not a model run/);
    expect(screen.getByTestId("sources").querySelectorAll("li")).toHaveLength(Object.keys(results.cap.sources).length);
    expect(screen.getByTestId("basis-list").textContent).toMatch(/What is measured/);
    expect(screen.getByTestId("basis-list").textContent).not.toMatch(/\bflow\b:/);
  });

  it("shows the fuel stress proxy and the payment cell on the bills tab", () => {
    window.history.replaceState(null, "", "/?tab=bills");
    render(<Dashboard data={results} />);
    expect(screen.getByTestId("tile-fuel-stress").textContent).toMatch(/%/);
    expect(screen.getByTestId("tile-payment-covers").textContent).toMatch(/%/);
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
