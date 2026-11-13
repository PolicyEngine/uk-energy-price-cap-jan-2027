"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { chartedMeasures } from "../utils/calculatorOnlyMeasures";
import { scenarioById } from "../utils/dataHelpers";
import { pageTitle } from "../utils/releaseMode";
import BillChangeChart from "./BillChangeChart";
import BillsSummary from "./BillsSummary";
import CapHistoryChart from "./CapHistoryChart";
import CapTiles from "./CapTiles";
import GroupChart from "./GroupChart";
import HouseholdCalculator from "./HouseholdCalculator";
import MethodologyTab from "./MethodologyTab";
import OfficialCostings from "./OfficialCostings";
import PolicyCards from "./PolicyCards";
import PolicySelector from "./PolicySelector";
import SupportCostChart from "./SupportCostChart";
import SupportDecileChart from "./SupportDecileChart";

export const REPO_URL = "https://github.com/PolicyEngine/uk-energy-price-cap-jan-2027";

// Flat tabs, as on the Autumn Budget 2026 dashboard. State lives in the
// address: ?tab=, ?sub=, ?scenario= and ?policies=.
export const VIEWS = [
  { value: "cap", label: "The cap" },
  { value: "bills", label: "Household bills", subs: ["deciles", "groups"] },
  { value: "support", label: "Support" },
  { value: "household", label: "Household examples" },
  { value: "policies", label: "Policies" },
  { value: "methodology", label: "Methodology" },
];
const SUB_LABELS = { deciles: "By income decile", groups: "By household group" };
const DEFAULT_VIEW = "cap";

/** Arrow keys, Home and End move between tabs (roving tabindex). */
function onTabKey(event, values, current, select, refs) {
  const keys = { ArrowRight: 1, ArrowLeft: -1 };
  let next;
  if (event.key in keys) {
    next = (values.indexOf(current) + keys[event.key] + values.length) % values.length;
  } else if (event.key === "Home") {
    next = 0;
  } else if (event.key === "End") {
    next = values.length - 1;
  } else {
    return;
  }
  event.preventDefault();
  select(values[next]);
  refs.current[values[next]]?.focus();
}

function readAddress(charted, scenarios, fallbackScenario) {
  // One measure by default: gains from several measures add up as if all
  // were introduced together, and alternatives rarely are.
  const base = { tab: DEFAULT_VIEW, sub: "deciles", scenario: fallbackScenario, policies: charted.slice(0, 1) };
  if (typeof window === "undefined") return base;
  const params = new URLSearchParams(window.location.search);
  const tab = VIEWS.some((v) => v.value === params.get("tab")) ? params.get("tab") : DEFAULT_VIEW;
  const sub = SUB_LABELS[params.get("sub")] ? params.get("sub") : "deciles";
  const scenario = scenarios.includes(params.get("scenario")) ? params.get("scenario") : fallbackScenario;
  const listed = params.get("policies")?.split(",").filter((id) => charted.includes(id));
  return { tab, sub, scenario, policies: listed?.length ? listed : base.policies };
}

export default function Dashboard({ data }) {
  const { meta, measures, cap } = data;
  const charted = useMemo(() => chartedMeasures(measures), [measures]);
  const chartedIds = useMemo(() => charted.map((m) => m.id), [charted]);
  const scenarioIds = useMemo(() => cap.scenarios.map((s) => s.id), [cap]);
  // The prerendered page is the default view; the address is read after
  // hydration, so the server and client render the same first frame (a
  // deep link read during hydration was React error 418).
  const [state, setState] = useState(() => ({
    tab: DEFAULT_VIEW,
    sub: "deciles",
    scenario: meta.default_scenario,
    policies: chartedIds.slice(0, 1),
  }));
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Read once, on mount: syncing from an external source (the address).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setState(readAddress(chartedIds, scenarioIds, meta.default_scenario));
    setReady(true);
  }, [chartedIds, scenarioIds, meta.default_scenario]);

  useEffect(() => {
    if (!ready) return;
    const params = new URLSearchParams();
    params.set("tab", state.tab);
    if (state.tab === "bills") params.set("sub", state.sub);
    if (state.scenario !== meta.default_scenario) params.set("scenario", state.scenario);
    if (state.tab === "support") params.set("policies", state.policies.join(","));
    window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
  }, [state, ready, chartedIds, meta.default_scenario]);

  const set = (patch) => setState((s) => ({ ...s, ...patch }));
  const tabRefs = useRef({});
  const subRefs = useRef({});
  const scenario = scenarioById(cap, state.scenario);
  const selected = charted.filter((m) => state.policies.includes(m.id));
  const summary = data.bills.summary?.find((r) => r.scenario_id === state.scenario);
  const selectedYear = selected[0]?.year;
  const yearLabel = meta.years.find((y) => y.year === selectedYear)?.label ?? "";

  return (
    <div className="app-shell min-h-screen">
      <div className="title-row">
        <div className="mx-auto max-w-[1200px] px-6 py-3">
          <h1>{pageTitle(meta.title)}</h1>
        </div>
      </div>
      <main className="relative z-[1] mx-auto max-w-[1200px] space-y-6 px-6 py-8">
        {/* While every figure is a placeholder the banner says so; this slot
            carries the run's own notice (the build and engine label) once it
            is not. */}
        {(!meta.placeholder || meta.source === "model") && (
          <p className="note-card rounded-xl p-4 text-sm" data-testid="run-note">
            {meta.notice}
          </p>
        )}
        <nav
          role="tablist"
          aria-label="Views"
          className="flex flex-wrap border-b border-slate-200"
          onKeyDown={(e) =>
            onTabKey(
              e,
              VIEWS.map((v) => v.value),
              state.tab,
              (tab) => set({ tab }),
              tabRefs,
            )
          }
        >
          {VIEWS.map((v) => (
            <button
              key={v.value}
              ref={(el) => {
                tabRefs.current[v.value] = el;
              }}
              type="button"
              role="tab"
              id={`tab-${v.value}`}
              aria-selected={state.tab === v.value}
              aria-controls={`panel-${v.value}`}
              tabIndex={state.tab === v.value ? 0 : -1}
              className={`tab-button${state.tab === v.value ? " active" : ""}`}
              onClick={() => set({ tab: v.value })}
            >
              {v.label}
            </button>
          ))}
        </nav>

        {["cap", "bills", "household"].includes(state.tab) && (
          <div className="flex flex-wrap items-center gap-2" role="group" aria-label="Cap scenario">
            <span className="text-sm text-slate-600">Cap for January to March 2027:</span>
            {cap.scenarios.map((s) => (
              <button
                key={s.id}
                type="button"
                aria-pressed={state.scenario === s.id}
                className={`toggle-button${state.scenario === s.id ? " active" : ""}`}
                onClick={() => set({ scenario: s.id })}
                data-testid="scenario-chip"
              >
                {s.label}
              </button>
            ))}
          </div>
        )}

        <div role="tabpanel" id={`panel-${state.tab}`} aria-labelledby={`tab-${state.tab}`} className="tab-body space-y-6">
          {state.tab === "cap" && (
            <>
              <CapTiles cap={cap} scenario={scenario} summary={summary} />
              <CapHistoryChart cap={cap} scenario={scenario} />
            </>
          )}
          {state.tab === "bills" && (
            <>
              <BillsSummary summary={summary} />
              <div
                role="tablist"
                aria-label="Household bills"
                className="flex gap-2"
                onKeyDown={(e) => onTabKey(e, VIEWS[1].subs, state.sub, (sub) => set({ sub }), subRefs)}
              >
                {VIEWS[1].subs.map((s) => (
                  <button
                    key={s}
                    ref={(el) => {
                      subRefs.current[s] = el;
                    }}
                    type="button"
                    role="tab"
                    id={`subtab-${s}`}
                    aria-controls={`subpanel-${s}`}
                    tabIndex={state.sub === s ? 0 : -1}
                    aria-selected={state.sub === s}
                    className={`tab-button sub-tab-button${state.sub === s ? " active" : ""}`}
                    onClick={() => set({ sub: s })}
                  >
                    {SUB_LABELS[s]}
                  </button>
                ))}
              </div>
              <div role="tabpanel" id={`subpanel-${state.sub}`} aria-labelledby={`subtab-${state.sub}`}>
                {state.sub === "deciles" && <BillChangeChart bills={data.bills} scenarioId={state.scenario} />}
                {state.sub === "groups" && <GroupChart bills={data.bills} scenarioId={state.scenario} />}
              </div>
            </>
          )}
          {state.tab === "support" && (
            <>
              <PolicySelector measures={charted} selected={state.policies} onChange={(policies) => set({ policies })} />
              <SupportCostChart measures={selected} years={meta.years} />
              <SupportDecileChart
                cells={data.decile_impact}
                selectedIds={selected.map((m) => m.id)}
                yearLabel={yearLabel}
              />
              <OfficialCostings official={data.official} years={meta.years} />
              <p className="text-sm text-slate-600">
                Measures with no figures are listed on the <a href="?tab=policies">Policies</a> tab with the reason.
              </p>
            </>
          )}
          {state.tab === "household" && (
            <HouseholdCalculator households={data.households} scenarioId={state.scenario} placeholder={meta.placeholder} />
          )}
          {state.tab === "policies" && <PolicyCards measures={measures} repoUrl={REPO_URL} />}
          {state.tab === "methodology" && (
            <MethodologyTab meta={meta} cap={cap} measures={measures} repoUrl={REPO_URL} />
          )}
        </div>
      </main>
    </div>
  );
}
