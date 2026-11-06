// Public wording for a measure's status and its not-computable reason.

export const STATUS_LABELS = {
  placeholder: "Placeholder",
  announced: "Announced",
  withdrawn: "Not announced",
};

export function statusLabel(status) {
  return STATUS_LABELS[status] ?? status;
}

/**
 * A reason without its trailing "(issue #N)", and the issue numbers it
 * named, so the page shows one plain sentence and a "details" link.
 */
export function splitReason(reason) {
  if (!reason) return { text: "", issues: [] };
  const issues = [...reason.matchAll(/issue #(\d+)/g)].map((m) => Number(m[1]));
  const text = reason
    .replace(/\s*\((?:issue|issues) #\d+(?:,? (?:and )?#\d+)*\)/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return { text, issues };
}

/** Link to the reform definitions at the commit the page was built from. */
export function definitionUrl(repoUrl, sha = process.env.NEXT_PUBLIC_COMMIT_SHA) {
  return sha ? `${repoUrl}/blob/${sha}/src/uk_energy_price_cap/reforms.py` : repoUrl;
}
