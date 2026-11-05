# Runbook: Ofgem cap announcement, 25 November 2026

Ofgem announces the cap for 1 January to 31 March 2027 on or before 25 November 2026. The wholesale observation window closes on 17 November. Times are relative to the announcement (T). One integrator pushes; nobody else commits.

## Before the day (by Friday 20 November)

- [ ] Engine and data pair certified, or the "unvalidated under this engine" label agreed (issue #1).
- [ ] Income measure chosen for support charts (issue #5).
- [ ] Spend level choice recorded in docs/METHOD.md (issue #7).
- [ ] Northern Ireland treatment fixed in the pipeline (issue #8).
- [ ] `pipeline.build_model` wired and run once on the frozen pair with the OBR path (expect a near-zero change against the baseline).
- [ ] Drill on Friday 13 November run and its retro filed (docs/DRILL.md).

## G0: freeze (by T−60 minutes)

Record in the PR: start commit SHA; policyengine-uk version; dataset name and SHA-256; certified pair or "unvalidated"; the declared basis (docs/METHOD.md).

## G1: coverage ledger (T to T+10)

From Ofgem's press release and summary letter, and any government statement the same day: one ledger line per item (`uk-energy-price-cap ledger` gives the starting list). Each line gets a route class and a cause class (docs/DRILL.md). Items already in the baseline are marked as such, not coded again.

## G2: provisional numbers (T+30)

Set `PLACEHOLDER_Q1_CAP` to Ofgem's Direct Debit level, confirm it is on the 2026 basis, and regenerate. Check:
- the typical household bill in `household.py` lands within £1 of Ofgem's level;
- one hand-checked household per coded measure;
- the bill change in aggregate against `data_inputs/expected_effects.csv`.

## G3: re-base and reconcile (T+40 to T+70)

With Annex 9 (rates by region and payment method): replace the single scaling in `household.py` with the published rates for each preset. Reconcile against official figures in `data_inputs/official/`; each gap over 10% gets a written reason.

## G5: inject (when it lands)

Any correction (Ofgem or government): rerun, new scoring SHA, re-run every hand-computed row, update ledger causes.

## G4: publication check

Not before two people have checked: MOCK or pre-release banner state, `noindex` (meta tag and `X-Robots-Tag`), `scripts/check_public_data.py` and `bun run check-public` clean, `meta.placeholder` set as intended, `sign_off.REQUIRED` switched only by the integrator. Nothing deploys from this repository yet: the deploy target is a team decision (`.github/workflows/deploy.yml`).
