"use client";

/**
 * Chips for the support measures that have figures; the list comes from
 * results.json. Measures from different fiscal years are never added
 * together: choosing one from another year starts a new selection.
 */
export default function PolicySelector({ measures, selected, onChange }) {
  const yearOf = (id) => measures.find((m) => m.id === id)?.year;
  const toggle = (id) => {
    if (selected.includes(id)) {
      const next = selected.filter((s) => s !== id);
      onChange(next.length ? next : [id]);
      return;
    }
    const sameYear = selected.every((s) => yearOf(s) === yearOf(id));
    onChange(sameYear ? [...selected, id] : [id]);
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
