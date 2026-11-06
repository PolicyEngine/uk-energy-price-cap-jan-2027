# Drill: Friday 13 November 2026, 10:00 to 12:30

This is a timed rehearsal of the announcement day for the Ofgem energy price cap for January to March 2027, run on a mock release. It follows the format of the Autumn Budget 2026 mock drills, using the compressed clock for days with two drills.

This file is the plan only. The mock release, documents, correction notice and answer key are held outside this repository by the drill owner. Only their SHA-256 hashes appear below. No file in this repository describes the mock content. Nothing from the packet is committed, before or after the drill.

This root `DRILL.md` is the only drill plan. On PR #9, `docs/DRILL.md` is a pointer to it with no hashes. A drill branch cut from the PR #9 head or from `main` does not carry this file until its first commit brings it in (Preconditions).

## Preconditions

- The template dashboard in PR #9 is merged by Thursday 12 November 2026, 17:00. If it is not, the drill branch is cut from the PR #9 head SHA, which is recorded in G0, and the deviation is logged.
- The drill branch is opened as a draft PR labelled `not for merge`. It is never stacked on another unmerged PR.
- The first commit on the drill branch is `git checkout origin/drill-plan -- DRILL.md`. The integrator then runs `uv run python scripts/check_packet_not_committed.py` and confirms it reports 8 packet hashes read. On a branch whose name contains `drill`, the script fails if the root `DRILL.md` is missing or lists no hashes, so name the branch `drill-...`.
- If G0 cannot name a certified engine and data pair (issue #1), the drill runs on the household calculator and the synthetic `results.json`. Every figure is then labelled "unvalidated under this engine", and national rows are scored on basis and gap class only.

## Roles (one person each)

| Role | Owns | Does not |
|---|---|---|
| Drill owner | the sealed packet, releases at the set times, the answer key | code, review or score |
| Integrator | the drill branch, the clock table, every commit, generation, re-basing | score households or open packet files before their release time |
| Reconciler | the coverage ledger, the reconciliation CSV, defects posted as PR comments within 5 minutes | push code |
| Scorer (the reconciler, after the documents) | specimen households, one commit SHA per scoring run | edit reform code |

Only the integrator pushes. The drill owner copies each file to the release folder, `~/drill7-release/`, at its slot and posts the file name, hash and time on the drill issue. The post never includes file contents. The release folder is outside the clone; nothing in it is copied into the repository. CI on the drill branch fails if any tracked file has the SHA-256 of a packet file (`scripts/check_packet_not_committed.py`).

## Clock (London time)

| Time | Release | Gate |
|---|---|---|
| by 09:00 | none | G0: freeze record in the drill PR (`make freeze DATASET=<file>` prints it): start SHA, the packet-guard line (8 hashes read), policyengine and policyengine-uk versions, dataset name and SHA-256, and the certified pair or "unvalidated" |
| 10:00 (T+0) | mock release (statement) | G1, 10:00 to 10:10: coverage ledger, each line routed |
| 10:30 (T+30) | none | G2: provisional numbers against the release figures, and one hand-checked household per coded measure |
| 10:40 (T+40) | documents: rates, costings, specimen households, blank scoring sheet | G3, to 11:10: re-base and reconcile; each gap over 10% has a written reason; update ledger causes |
| 11:15 (T+75) | inject: a correction notice | G5: rerun, re-score every hand-computed row, update ledger causes, new scoring SHA |
| 11:40 (T+100) | none | G4: local production build checked for the MOCK banner and `noindex` (command below) |
| 11:50 (T+110) | none | stop; log the stop commit |
| 12:00 (T+120) | answer key | scoring, to 12:15; the scorer checks the key's hash first |
| 12:15 | none | retro, to 12:30; filed on the drill issue the same day |

G0 is posted by 09:00, an hour before the release (T−60, as in `docs/RUNBOOK.md`), so the freeze is settled before anyone reads the packet.

## Route and cause classes (every ledger line gets one of each)

Route classes:
- `dashboard-param`: a parameter change in this repository
- `dashboard-structural`: a new modifier or variable in this repository
- `ledger`: not modelled; the figure is recorded
- `not-computable`: a data limit, recorded with the reason and never shown as £0
- `needs-pe-uk-first`: needs a change in policyengine-uk or the data

Where the fix belongs:
- **this dashboard repository:** `dashboard-param`, `dashboard-structural`, `ledger`
- **policyengine-uk:** `needs-pe-uk-first`, filed the same day as a draft
- **data (Microcosm):** `not-computable`, with the data limit named

Cause classes: `parameter`, `formula`, `data_calibration`, `basis`, `timing_fiscal_calendar`, `coverage`, `interaction`, `baseline_mismatch`.

The packet includes trap rows: items that are already in the baseline or already inside another line. Mark them as such in the ledger. Do not model them a second time.

## Basis, declared once in the PR at G1

- **Annual or quarterly:** say which, and hold it.
- **Fiscal or calendar year:** say which, and hold it.
- **Gross or net of support:** say which, and hold it.
- **Static or behavioural:** say which, and hold it.
- **Typical-consumption basis:** state which basis the cap levels and any ratio use (issue #3).
- **Country coverage:** state it for every figure, and say whether Northern Ireland is in or out.

## What to time and log

The clock table in the drill PR has one row per step, with the start time, the end time and the person. Machine time and people time are logged on separate lines.
- Machine time: generation, tests, build.
- People time: reading, coding, review.

Log these:
- the time each release was received, and its hash as checked
- each gate, with the time it was met or missed
- every commit SHA, and which SHA each scoring run used (one SHA per run)
- the time the inject was read, the time the rerun finished, and the new scoring SHA
- each defect posted by the reconciler: its time, and the time the integrator read it
- the stop commit

## MOCK and noindex rules

- Every page built in the drill shows a MOCK banner and carries `noindex`, in both the meta tag and the `X-Robots-Tag` header. Both are checked on the running production build, not on the dev server. The G4 build, from the repository root (pick a free port; `bun` runs `next`, which needs no `node` on the path):

  ```
  cd dashboard && NEXT_PUBLIC_MOCK=1 bun run build && bun run start -p 4873
  curl -sI http://localhost:4873/uk/energy-price-cap-jan-2027 | grep -i x-robots-tag
  MOCK=1 ../scripts/smoke-built-site.sh http://localhost:4873/uk/energy-price-cap-jan-2027
  ```

  The page lives under the base path; `/` alone is not the page. Stop the server by its PID afterwards.
- Nothing is deployed. There is no preview URL, Vercel, Modal or Cloud Run in this drill.
- `scripts/check_public_data.py` and `dashboard/scripts/check-public-files.mjs` pass on the stop commit.
- Registry measures keep their `placeholder` flag. No public file drops it.
- Mock figures never appear in this repository, its issues or its PRs. The drill PR records only process: gates, times, SHAs, ledger classes and the score by part.

## Rubric (100 points)

| Part | Points |
|---|---|
| Specimen households within ±1p of the key | 20 |
| National figures: basis and gap class | 30 |
| Ledger: route, cause and trap rows per line (scored on the final ledger at stop) | 25 |
| Publication path: banner, `noindex`, public-data checks, placeholder flag | 10 |
| Process: gates on time, one SHA per scoring run, inject logged, stop commit logged | 15 |

Rulings, so scoring is the same whoever scores:
- A `not-computable` line is scored on its route and its basis token (the data limit it names), not on a figure.
- The ledger is scored on the final ledger at the stop commit, so causes set at G1 and changed after G3 or the inject count as changed.
- Each trap row is scored yes or no: marked as already in the baseline (or inside another line), or not.

## Lessons carried from the Autumn Budget drills

1. One integrator. 2. Reviews as PR comments, read at once. 3. No stacking on unmerged PRs. 4. Reconciliation is a hard gate. 5. Declare the basis once. 6. Re-run hand-computed rows after an inject. 7. Statutory rounding (bills to the penny, half up). 8. Day-of measures go in this repository. 9. G0 names a certified pair or labels every figure unvalidated. 10. Charts read the measure list from the registry. 11. Check the banner and `noindex` on the built page, not on a dev server. 12. Data gaps go in the ledger first. 13. Time every step. 14. Update ledger causes after G3 and after the inject.

## Packet hashes (SHA-256)

The drill owner checks these before 09:00, and the scorer checks the key's hash at 12:00.

| File | Released at | SHA-256 |
|---|---|---|
| `T0_release.md` | 10:00 | `b660a82e3c4b862fa96ab512c50d03b048e33368ab006bf57fe743f6a91283d7` |
| `T40_documents.md` | 10:40 | `b6dd3d0a38a375409ed08741f0322256394e95d8203edcabe3a2203c3476481f` |
| `T40_scoring_sheet.csv` | 10:40 | `f7583abc9d8524753099b7169fd2097fab18706f25f93891126aebd7290c4a99` |
| `T75_inject.md` | 11:15 | `45208400129f3b3cb3968c719db86a949b7faf337047544cdacf7e8bf0a82dde` |
| `answer_key.md` | 12:00 | `52d654cf54f653e7faabfd78719bdfd1bbd61ac87948d93e7dba4b6dc2cddb96` |
| `answer_key.json` | 12:00 | `c1570c8e8b1e75a28bf3d1388cac343b1180e16f98a93126a28e07b814b60547` |
| `generate_key.py` | 12:00 | `39c18de138919880f3f46ae68f3638a0f5522878bb99cd6fd42e780f3d1c4e9a` |
| `OWNER_NOTES.md` | never (owner only) | `d1c513c0abe97c157afe51521e3e7f2d9f521a8c6569354ca57c763bf114bdd6` |

Check with `shasum -a 256 <file>`.
