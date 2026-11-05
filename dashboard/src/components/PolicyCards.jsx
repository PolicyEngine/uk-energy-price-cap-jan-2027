import { formatMillions } from "../utils/format";
import { policyDetail } from "../utils/policyDetails";

const ROUTE_LABELS = {
  "dashboard-param": "Modelled: parameter change",
  "dashboard-structural": "Modelled: structural change",
  ledger: "Recorded, not modelled",
  "not-computable": "Not computable",
  "needs-pe-uk-first": "Needs a model change first",
};

/** One card per measure in the registry, computable or not. */
export default function PolicyCards({ measures, repoUrl }) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {measures.map((m) => {
        const detail = policyDetail(m);
        return (
          <article key={m.id} className="panel" data-testid="policy-card">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="status-pill">{m.status}</span>
              <span className="status-pill">{ROUTE_LABELS[m.route] ?? m.route}</span>
            </div>
            <h3 className="text-lg font-semibold">{m.name}</h3>
            <p className="mt-1 text-sm text-slate-700">{m.description}</p>
            {detail && <p className="mt-2 text-sm">{detail}</p>}
            {m.computable ? (
              m.cost_gbp_m !== null && <p className="mt-2 text-sm">Cost: {formatMillions(m.cost_gbp_m)}</p>
            ) : (
              <p className="mt-2 text-sm text-slate-600" data-testid="limit-reason">
                {m.reason}
              </p>
            )}
            <a className="mt-2 inline-block text-sm" href={`${repoUrl}/blob/main/src/uk_energy_price_cap/reforms.py`}>
              Definition
            </a>
          </article>
        );
      })}
    </div>
  );
}
