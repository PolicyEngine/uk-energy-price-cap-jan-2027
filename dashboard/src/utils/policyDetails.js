// Card text for each measure, keyed by id. A card's text is used only if
// the registry description still matches the one it was written for, so a
// changed measure never shows stale text (Autumn Budget repo, #144).
// PLACEHOLDER: no card text is written until the cap is announced.
export const POLICY_DETAILS = {
  // hep_top_up: {
  //   writtenFor: "<registry description>",
  //   summary: "...",
  // },
};

/** The card's extra text, or null if none or if it is stale. */
export function policyDetail(measure, details = POLICY_DETAILS) {
  const entry = details[measure.id];
  if (!entry || entry.writtenFor !== measure.description) return null;
  return entry.summary;
}
