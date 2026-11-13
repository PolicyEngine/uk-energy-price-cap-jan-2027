import { formatMillions } from "../utils/format";
import { definitionUrl, splitReason, statusLabel } from "../utils/measureText";
import { policyDetail } from "../utils/policyDetails";

const ROUTE_LABELS = {
  "dashboard-param": "Modelled: parameter change",
  "dashboard-structural": "Modelled: structural change",
  ledger: "Recorded, not modelled",
  "not-computable": "Not computable",
  "needs-pe-uk-first": "Needs a model change first",
};

/** One card per measure in the registry, computable or not. Reasons live here only. */
export default function PolicyCards({ measures, repoUrl }) {
  const definitions = definitionUrl(repoUrl);
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {measures.map((m) => {
        const detail = policyDetail(m);
        const reason = splitReason(m.reason);
        return (
          <article key={m.id} id={`measure-${m.id}`} className="panel" data-testid="policy-card">
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="status-pill">{statusLabel(m.status)}</span>
              <span className="status-pill">{ROUTE_LABELS[m.route] ?? m.route}</span>
            </div>
            <h3 className="text-lg font-semibold">{m.name}</h3>
            <p className="mt-1 text-sm text-slate-700">{m.description}</p>
            {detail && <p className="mt-2 text-sm">{detail}</p>}
            {m.computable ? (
              m.lever === "bills" ? (
                m.households_reached_m !== null && (
                  <p className="mt-2 text-sm" data-testid="bills-reach">
                    Households paying less: {m.households_reached_m.toFixed(1)}m
                  </p>
                )
              ) : (
                m.cost_gbp_m !== null && <p className="mt-2 text-sm">Cost: {formatMillions(m.cost_gbp_m)}</p>
              )
            ) : (
              <p className="mt-2 text-sm text-slate-600" data-testid="limit-reason">
                {reason.text}
                {reason.issues.map((n) => (
                  <span key={n}>
                    {" "}
                    <a href={`${repoUrl}/issues/${n}`}>Details</a>
                  </span>
                ))}
              </p>
            )}
            <a className="mt-2 inline-block text-sm" href={definitions}>
              Definition
            </a>
          </article>
        );
      })}
    </div>
  );
}
