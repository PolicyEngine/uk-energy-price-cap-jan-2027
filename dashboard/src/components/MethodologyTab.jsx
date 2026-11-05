/** Method, basis and versions. Each fact appears here once; other tabs link here. */
export default function MethodologyTab({ meta, measures, repoUrl }) {
  const notComputable = measures.filter((m) => !m.computable);
  return (
    <div className="space-y-6">
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Method</h3>
        <p className="text-sm text-slate-700">
          PolicyEngine UK, a static microsimulation model of the UK tax and benefit system, runs on Microcosm,
          PolicyEngine&apos;s calibrated survey-based dataset. Microcosm holds household spending on electricity and gas
          in pounds. The cap shock moves that spending by the change in prices; support measures are changes to model
          parameters. Households do not change how much energy they use. Northern Ireland is outside the Ofgem cap.
        </p>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Basis</h3>
        <ul className="list-disc pl-5 text-sm text-slate-700">
          {Object.entries(meta.basis).map(([k, v]) => (
            <li key={k}>
              <strong>{k}</strong>: {v}
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">What is not modelled, and why</h3>
        <ul className="list-disc pl-5 text-sm text-slate-700">
          {notComputable.map((m) => (
            <li key={m.id}>
              <strong>{m.name}</strong>: {m.reason}
            </li>
          ))}
        </ul>
      </section>
      <section className="panel">
        <h3 className="mb-2 text-lg font-semibold">Replication</h3>
        <p className="text-sm text-slate-700" data-testid="replication">
          policyengine-uk: {meta.engine.policyengine_uk}. Dataset: {meta.engine.dataset}.{" "}
          {meta.engine.validated ? "Certified engine and data pair." : "Unvalidated under this engine."} Code:{" "}
          <a href={repoUrl}>{repoUrl.replace("https://", "")}</a>.
        </p>
      </section>
    </div>
  );
}
