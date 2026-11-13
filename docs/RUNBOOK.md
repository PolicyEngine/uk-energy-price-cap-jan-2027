# Runbook: Ofgem cap announcement, 25 November 2026

Ofgem announces the cap for 1 January to 31 March 2027 on or before 25 November 2026. The wholesale observation window closes on 17 November. Times are relative to the announcement (T). One integrator pushes; nobody else commits. The one-page version is [event-day-checklist.md](event-day-checklist.md). Each gate has one `make` target.

## Before the day (by Friday 20 November)

- [ ] Engine and data pair fixed in `data_build.DATA_BUILD` and labelled "build uk-frs-calibration-attempt-20261110T204756Z-9e18f010, policyengine-uk 2.177.7, not in a policyengine.py release" (issue #1); switch to build `…-6f918b81` if it is published first.
- [ ] Income measure for support charts confirmed (issue #5; docs/METHOD.md states the current choice).
- [ ] Spend level choice recorded in docs/METHOD.md (issue #7).
- [ ] Northern Ireland treatment checked in the pipeline (issue #8).
- [ ] `uk-energy-price-cap generate --source model --allow-unmanaged --dataset <file>` run once on the frozen pair, alone on the machine. The run takes the machine-wide lock itself (`heavy.py`: the file `/tmp/pe-heavy.lock` holding "<pid> uk-energy-price-cap-generate", created with noclobber and removed only by its owner) and waits for 22 GB of free+inactive memory before the first simulation; it waits, without loading anything, while another job holds the lock. The manifest's cap-lever check for the OBR path scenario must be about zero.
- [ ] Drill on Friday 13 November run and its retro filed (plan: https://github.com/PolicyEngine/uk-energy-price-cap-jan-2027/blob/drill-plan/DRILL.md).

## Ledger classes (G1)

Route: `dashboard-param` (a parameter change here), `dashboard-structural` (a new modifier or variable here), `ledger` (not modelled; the figure is recorded), `not-computable` (a data limit, with the reason, never £0), `needs-pe-uk-first` (filed upstream the same day).

Cause: `parameter`, `formula`, `data_calibration`, `basis`, `timing_fiscal_calendar`, `coverage`, `interaction`, `baseline_mismatch`.

Status: `announced` (published with figures), `withdrawn` (a candidate lever not announced: the ledger line and card stay, with no figures; no registry entry is deleted), `placeholder` (holds the whole file back as a placeholder).

## G0: freeze (by T−60 minutes)

`make freeze DATASET=<file>` prints the record. Post it in the PR: start commit SHA; installed policyengine, policyengine-uk and policyengine-core versions; dataset build id and SHA-256 (the record shows `dataset_problem` or `engine_problem` if either differs from `DATA_BUILD`); the label; the declared basis (docs/METHOD.md).

## G1: coverage ledger (T to T+10)

From Ofgem's press release and summary letter, and any government statement the same day: one ledger line per item (`make ledger` gives the starting list). Each line gets a route class and a cause class (above). Items already in the baseline are marked as such, not coded again.

## G2: provisional numbers (T+30)

Set `PLACEHOLDER_Q1_CAP` to Ofgem's Direct Debit level, confirm it is on the 2026 basis, replace the scenario rows in `cap_levels.json` with that one level, set each announced measure's status, and `make generate`. Check:
- the typical household bill in `household.py` lands within £1 of Ofgem's level;
- one hand-checked household per coded measure;
- the bill change in aggregate against `data_inputs/expected_effects.csv`.

## G3: re-base and reconcile (T+40 to T+70)

With Annex 9 (rates by region and payment method): replace the single scaling in `household.py` with the published rates for each preset. Reconcile against official figures in `data_inputs/official/`; each gap over 10% gets a written reason. Update ledger causes.

## G5: correction (when it lands)

1. Record the time the correction was read.
2. If the published page is wrong, withdraw first: set the affected measures to `withdrawn` (or revert the publish commit, below) and regenerate, so no wrong figure stays up while the fix is made.
3. Fix the input (the cap level, a measure value or a rate) in one commit.
4. `make generate` and `make check`: a new results SHA-256 in `manifest.json`.
5. Re-run every hand-computed household and update ledger causes.
6. Rebuild and re-check the page (G4).
7. Log the new scoring SHA and the time the rerun finished.

## G4: publication check and going public

Checked on the local production build, never on a dev server or a preview: `make build`, then `cd dashboard && bun run start -p 4871`, then `curl -sI http://localhost:4871/uk/energy-price-cap-jan-2027` shows `X-Robots-Tag: noindex, nofollow` and the HTML has the meta robots tag and the banner. In a drill the build is `NEXT_PUBLIC_MOCK=1` and the banner reads MOCK. Two people check the banner, `noindex`, `make check` (both public-data checks and the manifest), `meta.placeholder` set as intended, and `sign_off.REQUIRED` switched only by the integrator.

Going public is one commit, with its tests, so it can be reverted in one step:
- `dashboard/app/layout.jsx`: drop `<PreReleaseBanner />` and the `robots` block; add the canonical address (`alternates.canonical`).
- `dashboard/next.config.mjs`: drop the `X-Robots-Tag` header.
- `dashboard/src/components/PreReleaseBanner.test.jsx`: invert the three tests (no banner, no `noindex`).
- `src/uk_energy_price_cap/sign_off.py`: `REQUIRED = False`.

## Rollback

Nothing deploys from this repository yet: the deploy target is a team decision (`.github/workflows/deploy.yml`). Until it exists, rollback is `git revert -m 1 <merge commit>` of the publish PR on `main`, then regenerate and rebuild. When a Vercel project exists, add its instant rollback and promote steps here.
