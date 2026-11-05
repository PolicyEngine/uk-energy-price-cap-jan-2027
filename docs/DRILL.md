# Drill: Friday 13 November 2026, 10:00 to 12:30

A timed rehearsal of the announcement day on a mock Ofgem release. Format from the Autumn Budget 2026 drills, compressed to fit two drills a day.

## Packet hygiene

- The drill owner prepares the packet and the answer key **outside this repository**. Only their SHA-256 hashes go in `data_inputs/packet/HASHES.md`, committed before 09:30.
- Files are released at the set times below, not the night before.
- The answer key is attached at key time and the scorer checks its hash.
- The drill runs on a branch cut from `template-dashboard` (or `main` once it merges), opened as a draft PR labelled `not for merge`, never stacked on another unmerged PR.
- Every page built in the drill shows a MOCK banner and `noindex`.

## Roles (one person each)

| Role | Owns | Does not |
|---|---|---|
| Integrator | branch, clock table, every commit, generation, re-basing | score households |
| Reconciler | ledger, reconciliation CSV, defects posted as PR comments within 5 minutes | push code |
| Scorer (the reconciler, after the documents) | specimen households, one commit SHA per scoring run | edit reform code |

## Clock

| Time | Release | Gate |
|---|---|---|
| by 09:45 | none | G0: freeze record in the PR (start SHA, policyengine-uk version, dataset name and SHA-256, certified pair or "unvalidated") |
| 10:00 | mock press release and summary letter (cap by payment method, cost shares) | G1 (10:00 to 10:10): coverage ledger, each line routed |
| 10:30 | none | G2: provisional numbers against the release figures, plus one hand-checked household per coded measure |
| 10:40 | documents: mock rates by region and payment method, mock official specimen bills, blank scoring sheet | G3 (to 11:10): re-base and reconcile; each gap over 10% has a written reason |
| 11:15 | inject: a correction notice | G5: rerun, new scoring SHA |
| 11:40 | none | G4: local production build (`bun run build && bun run start`) checked for the banner and `noindex` |
| 11:50 | none | stop; log the stop commit |
| 12:00 | answer key | scoring (to 12:15) |
| 12:15 | none | retro (to 12:30); filed as an issue the same day |

Machine time and people time are logged apart on the clock table (generation, tests and build against reading, coding and review).

## Ledger classes

Route: `dashboard-param`, `dashboard-structural`, `ledger` (not modelled, figure recorded), `not-computable` (data limit, with reason), `needs-pe-uk-first`.

Cause: `parameter`, `formula`, `data_calibration`, `basis`, `timing_fiscal_calendar`, `coverage`, `interaction`, `baseline_mismatch`.

## Rubric (100 points)

| Part | Points |
|---|---|
| Specimen households within ±1p of the key | 20 |
| National figures: basis and gap class | 30 |
| Ledger: class, route and cause per line | 25 |
| Publication path (banner, `noindex`, public-data checks, placeholder flag) | 10 |
| Process: gates on time, one SHA per run, inject logged | 15 |

The packet includes trap rows: items in the release that are already in the baseline.

## What the drill tests for this event

- The cap level is read on the right typical-consumption basis.
- The cap shock moves both fuels; Northern Ireland is excluded.
- Annual against quarterly figures, and fiscal against calendar years, are declared once and held.
- Bills on a payment method other than Direct Debit use that method's rates.
- Support already in the baseline is not counted twice.
- A lever the data cannot carry is published as not computable, never as £0.

## Lessons carried from the Autumn Budget drills

1. One integrator. 2. Reviews as PR comments, read at once. 3. No stacking on unmerged PRs. 4. Reconciliation is a hard gate. 5. Declare the basis once. 6. Re-run hand-computed rows after an inject. 7. Statutory rounding (bills to the penny, half up). 8. Day-of measures go in this repository. 9. G0 names a certified pair or labels every figure unvalidated. 10. Charts read the measure list from the registry. 11. Check the banner and `noindex` on the built page, not on a dev server. 12. Data gaps go in the ledger first. 13. Time every step.
