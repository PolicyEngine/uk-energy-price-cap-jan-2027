const BASIS_LABELS = {
  bills: "Bills",
  year: "Year",
  flow: "What is measured",
  behaviour: "Behaviour",
  support: "Support",
};

const SOURCE_LABELS = {
  levels: "Cap levels",
  rates: "Unit rates and standing charges",
  obr_path: "Forecast path in the model",
  range: "Planning range",
};

function sentence(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : text;
}

/** Method, basis, sources and versions. Each fact appears here once; other tabs link here. */
export default function MethodologyTab({ meta, cap, measures, repoUrl }) {
  const notComputable = measures.filter((m) => !m.computable);
  const commit = process.env.NEXT_PUBLIC_COMMIT_SHA;
  const engine = meta.engine;
  return (
    <div className="space-y-6">
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Method</h3>
        <p className="text-sm text-slate-700">
          PolicyEngine UK, a static microsimulation model of the UK tax and benefit system, runs on Microcosm,
          PolicyEngine&apos;s calibrated survey-based dataset. Microcosm holds household spending on electricity and gas
          in pounds. Bill changes apply the ratio of Ofgem&apos;s January to March 2027 level to its October to
          December 2026 level to that spending; support measures are changes to model parameters. Households do not
          change how much energy they use. Northern Ireland is outside the Ofgem cap. Microcosm sets energy spend above
          ONS household spending; the size of the gap depends on the data build (
          <a href={`${repoUrl}/issues/7`}>details</a>). Ofgem&apos;s Market Stabilisation Charge, if activated, does not
          change the cap level.
        </p>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Basis</h3>
        <ul className="list-disc pl-5 text-sm text-slate-700" data-testid="basis-list">
          {Object.entries(meta.basis).map(([k, v]) => (
            <li key={k}>
              <strong>{BASIS_LABELS[k] ?? sentence(k)}</strong>: {v}
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">What is not modelled</h3>
        <p className="text-sm text-slate-700">
          {notComputable.length} measures have no figures; each card on the <a href="?tab=policies">Policies</a> tab
          gives the reason. They are shown as not computable, never as £0.
        </p>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Sources</h3>
        <ul className="list-disc pl-5 text-sm text-slate-700" data-testid="sources">
          {Object.entries(cap.sources).map(([k, v]) => (
            <li key={k}>
              <strong>{SOURCE_LABELS[k] ?? sentence(k)}</strong>:{" "}
              {v.url ? <a href={v.url}>{v.label}</a> : v.label ?? v}
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Replication</h3>
        <p className="text-sm text-slate-700" data-testid="replication">
          policyengine-uk: {engine.policyengine_uk}. Dataset: {engine.dataset}
          {engine.dataset_sha256 ? ` (SHA-256 ${engine.dataset_sha256.slice(0, 12)})` : ""}.{" "}
          {engine.validated ? "Certified engine and data pair." : "Unvalidated under this engine."} Code:{" "}
          <a href={commit ? `${repoUrl}/tree/${commit}` : repoUrl}>
            {repoUrl.replace("https://", "")}
            {commit ? ` at ${commit.slice(0, 7)}` : ""}
          </a>
          .
        </p>
      </section>
    </div>
  );
}
