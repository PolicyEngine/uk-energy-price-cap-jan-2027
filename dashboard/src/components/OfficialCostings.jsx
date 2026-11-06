/** Official costings of the support already in place (data_inputs/official). */
export default function OfficialCostings({ official, years }) {
  if (!official?.length) return null;
  const label = (y) => years.find((x) => x.year === y)?.label ?? `${y}-${String((y + 1) % 100).padStart(2, "0")}`;
  return (
    <section className="panel" aria-label="Official costings">
      <h3 className="mb-2 text-lg font-semibold">Official costings of support already in place</h3>
      <table className="data-table compact" data-testid="official-costings">
        <thead>
          <tr>
            <th>Measure</th>
            <th>Year</th>
            <th>Cost</th>
            <th>Source</th>
          </tr>
        </thead>
        <tbody>
          {official.map((c) => (
            <tr key={`${c.id}-${c.year}`}>
              <td>{c.name}</td>
              <td>{label(c.year)}</td>
              <td>£{c.cost_gbp_bn.toFixed(1)}bn</td>
              <td>
                <a href={c.url}>{c.source}</a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 text-sm text-slate-600">
        These measures are already in the model&apos;s baseline, so the chart above shows only changes to them.
      </p>
    </section>
  );
}
