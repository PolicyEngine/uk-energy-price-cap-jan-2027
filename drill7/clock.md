# Drill 7 clock (Fri 13 Nov 2026, London time)

Integrator, reconciler and scorer: one agent holds all three roles (deviation from DRILL.md "one person each"; recorded at G0).
All figures: build uk-frs-calibration-attempt-20261112T133744Z-6f918b81, policyengine-uk 2.177.7, not in a policyengine.py release.

## Deviations and process misses

- **PROCESS MISS: integrator started at 10:53, 53 minutes after T+0 (10:00).** G0 (due 09:00), G1 (due 10:10) and G2 (due 10:30) were all met late; times below are real, not backdated.
- One agent holds integrator, reconciler and scorer.
- No drill PR and no push: by instruction, the drill7-run branch stays local (packet content in drill7/). G0 and gate records live in this file instead of PR comments. Reconciler defects are logged here, not as PR comments.
- At 10:53 the integrator's first directory listing included `~/drill7-work/`, exposing the file names `release.sh` and `release.log` (sizes and times only; contents not read). Not listed again.
- needs-pe-uk-first lines (L03, L15) are not filed upstream today: no GitHub posting in this drill. To file as drafts when Vahid decides.

## Releases received

| Release | Received | SHA-256 checked | Matches DRILL.md |
|---|---|---|---|
| T0_release.md | read 10:53 (released 10:00) | b660a82e…283d7 | yes |
| T40_documents.md | read 10:53 (released 10:40) | b6dd3d0a…6481f | yes |
| T40_scoring_sheet.csv | read 10:53 (released 10:40) | f7583abc…c4a99 | yes |

## Gates

| Gate | Due | Met | Status | Evidence |
|---|---|---|---|---|
| G0 freeze | 09:00 | 10:53:36 | MISSED (late 113 min) | start SHA 30f5a47 (PR #18 head, open, not merged); drill plan commit 5fe26ed; `make freeze` clean, managed false, certified false, no dataset_problem / engine_problem; policyengine-uk 2.177.7, core 3.34.10, policyengine none; dataset uk-frs-calibration-attempt-20261112T133744Z-6f918b81 sha256 e268e3af7932784ad4471f008097a5acc6c3c5bc15c4c54fbb5a489b2a0ac9ae; build_manifest engine policyengine-uk 2.177.7 / core 3.34.10 (pair matches); packet guard: "branch drill7-run: 9 packet hash(es) read, 0 problem(s)"; lock free; free+inactive about 26 GB |
| G1 ledger | 10:10 | 11:04 | MISSED (late 54 min) | drill7/ledger.csv, 21 lines, each routed with route and cause; trap rows marked |
| G2 provisional + hand checks | 10:30 | 11:02 | MISSED (late 32 min) | registry commit 808c8e7; typical bill from GB-average rates 2,027.26 vs level 2,027 (within £1); hand checks below |
| G3 re-base and reconcile | 11:10 | 11:06 | MET | ledger + reconciliation commit c889c50; gaps over 10% with written reasons: N5 (timing), N6 (data_calibration), N10 (data_calibration), N11 (timing); cause vs gap scan done (only N7/L15 share `coverage`, justified in N7). Dashboard calculator presets not re-based (L02 note) |

### G2 hand checks (one per coded measure)

| Measure | Check | Result |
|---|---|---|
| cap_q1_2027 | typical DD bill from GB-average rates (S1) vs the level | 2,027.26 vs 2,027 (within £1); Oct-Dec 1,723.61 vs 1,723 |
| hep_second_apr_2027 | engine single household, England band B, 2027-28 | 0 to 100 (exactly £100) |
| whd_uplift | engine single household with Pension Credit, 2026-27 | 150 to 250 |
| hep_great_britain | engine single household, Scotland band B, 2026-27 | 0 to 100 |

## Machine time

| Step | Start | End | Notes |
|---|---|---|---|
| uv sync --locked --extra dev --extra model | 10:53 | 10:54 | |
| make freeze | 10:53:35 | 10:53:36 | |
| pytest (full, incl. engine) | 10:56 | 11:01 | three runs while fixing drill-day test pins |
| National run `make generate DATASET=…` at 08e0b8b | 11:01:48 | 11:04:52 | 184 s wall; peak RSS 14.9 GB; took and released /tmp/pe-heavy.lock (pid 55262); receipt dataset_sha256 e268e3af…c9ae = G0 SHA; meta.placeholder true; cap lever check obr_path 0.000, central 1.525 bn |
| make check | 11:06:05 | 11:06:09 | validate 0, check_public_data 0, check-public 0 |

## People time

| Step | Start | End |
|---|---|---|
| Read DRILL.md, lessons, RUNBOOK, packet T0 + T40 | 10:53 | 10:55 |
| Registry and tests to the release | 10:55 | 11:01 |
| Specimen scorer and G3 scoring | 11:01 | 11:02:35 |
| Ledger | 11:02:40 | 11:04 |
| Reconciliation | 11:05 | 11:06 |

## Commits

| SHA | Time | What |
|---|---|---|
| 30f5a47 | – | start (origin/engine-2.177.7-microcosm-9e18f010, PR #18 head, open) |
| 5fe26ed | 10:53:32 | DRILL.md from drill-plan |
| 808c8e7 | 11:01:42 | registry to the release |
| 08e0b8b | 11:01:48 | placeholder manifest; national run commit |
| 190552d | 11:02:29 | specimen scorer + inputs |
| beffdf1 | 11:02:35 | S7 note fix; **scoring run 1 (G3) SHA** |
| 3f3c5d5 | 11:02:35 | households_G3.csv (scored at beffdf1) |
| c889c50 | 11:06:11 | national results, ledger, reconciliation |

## Scoring runs (one SHA per run)

| Run | SHA | Output |
|---|---|---|
| 1 (G3) | beffdf1 | drill7/households_G3.csv |

## Defects (reconciler)

| Time found | Defect | Time read by integrator | Fix |
|---|---|---|---|
| 11:02 | S7 alternative-net note had an arithmetic slip (204.65 vs 203.65) before scoring run 1 | 11:02 | beffdf1 (scored figures unaffected) |
