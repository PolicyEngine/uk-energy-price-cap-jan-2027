"use client";

/** Chips for the support measures that have figures; the list comes from results.json. */
export default function PolicySelector({ measures, selected, onChange }) {
  const toggle = (id) => {
    const next = selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id];
    onChange(next);
  };
  return (
    <div className="flex flex-wrap gap-2" role="group" aria-label="Measures">
      {measures.map((m) => (
        <button
          key={m.id}
          type="button"
          aria-pressed={selected.includes(m.id)}
          className={`toggle-button${selected.includes(m.id) ? " active" : ""}`}
          onClick={() => toggle(m.id)}
          data-testid="policy-chip"
        >
          {m.name}
        </button>
      ))}
    </div>
  );
}
