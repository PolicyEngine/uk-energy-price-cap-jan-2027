"use client";

import { useEffect, useMemo, useState } from "react";
import { chartedMeasures } from "../utils/calculatorOnlyMeasures";
import { scenarioById } from "../utils/dataHelpers";
import BillChangeChart from "./BillChangeChart";
import CapHistoryChart from "./CapHistoryChart";
import CapTiles from "./CapTiles";
import GroupChart from "./GroupChart";
import HouseholdCalculator from "./HouseholdCalculator";
import MethodologyTab from "./MethodologyTab";
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

function readAddress(charted, scenarios, fallbackScenario) {
  const base = { tab: DEFAULT_VIEW, sub: "deciles", scenario: fallbackScenario, policies: charted };
  if (typeof window === "undefined") return base;
  const params = new URLSearchParams(window.location.search);
  const tab = VIEWS.some((v) => v.value === params.get("tab")) ? params.get("tab") : DEFAULT_VIEW;
  const sub = SUB_LABELS[params.get("sub")] ? params.get("sub") : "deciles";
  const scenario = scenarios.includes(params.get("scenario")) ? params.get("scenario") : fallbackScenario;
  const listed = params.get("policies")?.split(",").filter((id) => charted.includes(id));
  return { tab, sub, scenario, policies: listed?.length ? listed : charted };
}

export default function Dashboard({ data }) {
  const { meta, measures, cap } = data;
  const charted = useMemo(() => chartedMeasures(measures), [measures]);
  const chartedIds = useMemo(() => charted.map((m) => m.id), [charted]);
  const scenarioIds = useMemo(() => cap.scenarios.map((s) => s.id), [cap]);
  const [state, setState] = useState(() => readAddress(chartedIds, scenarioIds, meta.default_scenario));

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("tab", state.tab);
    if (state.tab === "bills") params.set("sub", state.sub);
    if (state.scenario !== meta.default_scenario) params.set("scenario", state.scenario);
    if (state.policies.length !== chartedIds.length) params.set("policies", state.policies.join(","));
    window.history.replaceState(null, "", `${window.location.pathname}?${params}`);
  }, [state, chartedIds, meta.default_scenario]);

  const set = (patch) => setState((s) => ({ ...s, ...patch }));
  const scenario = scenarioById(cap, state.scenario);
  const selected = charted.filter((m) => state.policies.includes(m.id));

  return (
    <div className="app-shell min-h-screen">
      <div className="title-row">
        <div className="mx-auto max-w-[1200px] px-6 py-3">
          <h1>{meta.title}</h1>
        </div>
      </div>
      <main className="relative z-[1] mx-auto max-w-[1200px] space-y-6 px-6 py-8">
        <p className="note-card rounded-xl p-4 text-sm" data-testid="placeholder-note">
          {meta.notice}
        </p>
        <nav role="tablist" aria-label="Views" className="flex flex-wrap border-b border-slate-200">
          {VIEWS.map((v) => (
            <button
              key={v.value}
              type="button"
              role="tab"
              id={`tab-${v.value}`}
              aria-selected={state.tab === v.value}
              aria-controls={`panel-${v.value}`}
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
              <CapTiles cap={cap} scenario={scenario} />
              <CapHistoryChart cap={cap} scenario={scenario} />
            </>
          )}
          {state.tab === "bills" && (
            <>
              <div role="tablist" aria-label="Household bills" className="flex gap-2">
                {VIEWS[1].subs.map((s) => (
                  <button
                    key={s}
                    type="button"
                    role="tab"
                    aria-selected={state.sub === s}
                    className={`tab-button sub-tab-button${state.sub === s ? " active" : ""}`}
                    onClick={() => set({ sub: s })}
                  >
                    {SUB_LABELS[s]}
                  </button>
                ))}
              </div>
              {state.sub === "deciles" && <BillChangeChart bills={data.bills} scenarioId={state.scenario} />}
              {state.sub === "groups" && <GroupChart bills={data.bills} scenarioId={state.scenario} />}
            </>
          )}
          {state.tab === "support" && (
            <>
              <PolicySelector measures={charted} selected={state.policies} onChange={(policies) => set({ policies })} />
              <SupportCostChart measures={selected} years={meta.years} />
              <SupportDecileChart cells={data.decile_impact} selectedIds={selected.map((m) => m.id)} />
              <p className="text-sm text-slate-600">
                Measures with no figures are listed on the <a href="?tab=policies">Policies</a> tab with the reason.
              </p>
            </>
          )}
          {state.tab === "household" && (
            <HouseholdCalculator households={data.households} scenarioId={state.scenario} placeholder={meta.placeholder} />
          )}
          {state.tab === "policies" && <PolicyCards measures={measures} repoUrl={REPO_URL} />}
          {state.tab === "methodology" && <MethodologyTab meta={meta} measures={measures} repoUrl={REPO_URL} />}
        </div>
      </main>
    </div>
  );
}
