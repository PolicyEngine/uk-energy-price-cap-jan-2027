# Drill: Sunday 15 November 2026, 23:00–01:30

A timed rehearsal of Ofgem's announcement of the energy price cap for 1 January to 31 March 2027 (due on or before 25 November 2026), and of any government support announced with it, on a mock packet. All times are London time. Times after midnight are Monday 16 November.

This file holds the plan only. It is the only copy of the clock and the packet hashes; the drill issue links here. It says nothing about the mock content. The statement, documents, correction or inject, answer key and scoring tool are held outside this repository by the drill owner and released at the times below. Nothing from the packet is committed, before or after the drill.

## Preconditions

- The drill branch is a local run branch named `drill-11-...`, cut from the head of `engine-2.177.7-microcosm-9e18f010`. That branch is on build 6f918b81 despite its name, so the cut head must include 30f5a47. Its first commit brings this file in:

  ```
  git checkout origin/drill-plan-11 -- DRILL.md
  git commit -m "Bring the drill 11 plan onto the drill branch"
  uv run python scripts/check_packet_not_committed.py
  ```

  The guard must report 13 packet hashes read: the 12 packet files in the table below plus the dataset SHA-256, because it counts every SHA-256 in this file. The head SHA the branch was cut from is recorded in G0.
- **The drill PR is opened first, before G0.** It is a draft PR from the run branch, labelled `not for merge`, and it is never merged. G0, every gate record, every defect and `FREEZE.txt` are posted on it as comments.
- Only the integrator pushes.

## Engine and data pair

The pair:
- policyengine-uk 2.177.7;
- policyengine-core 3.34.10 (no policyengine.py);
- Microcosm build `uk-frs-calibration-attempt-20261112T133744Z-6f918b81`, SHA-256 `e268e3af7932784ad4471f008097a5acc6c3c5bc15c4c54fbb5a489b2a0ac9ae`, made on 2.177.7.

No policyengine.py release covers this pair, so every figure carries the label "build uk-frs-calibration-attempt-20261112T133744Z-6f918b81, policyengine-uk 2.177.7, not in a policyengine.py release". That label stands in for "unvalidated under this engine" wherever the key names it.

policyengine.py 6.19.0 pins policyengine-uk 2.174.1 with build eeb6093e, a different certified pair. Running eeb6093e under 2.177.7, or 6f918b81 under 2.174.1, is a mixed pair: it is invalid and its figures are not scored. Figures from any pair not recorded at G0 are not scored.

## Clock

| Time | T | Release | Gate |
|---|---|---|---|
| by 22:30 | T−30 | none | **G0**: pair record posted as a comment on the drill PR |
| 23:00 | T+0 | statement | |
| 23:10 | T+10 | none | **G1**: coverage ledger, every line routed, with a cause class; items already in the baseline flagged |
| 23:10–23:20 | | none | heavy slot (G2) |
| 23:30 | T+30 | none | **G2**: provisional numbers, basis declared once, one hand-checked household per coded measure |
| 23:40 | T+40 | documents: costings, household basis, example households, blank scoring sheet | |
| 00:10 | T+70 | none | **G3**: re-base and reconcile; each gap over 10% has a written reason and a gap class; ledger causes updated |
| 00:15 | T+75 | correction notice | |
| 00:15–00:40 | | none | heavy slot (G5 and the G4 build) |
| 00:35 | T+95 | none | **G5**: re-run everything affected; every hand row re-run into its own file; new scoring SHA |
| 00:40 | T+100 | none | **G4**: local production build checked |
| 00:50 | T+110 | none | **stop**: stop commit logged; nothing scored changes after it |
| 00:55 | T+115 | none | **`FREEZE.txt`** posted on the drill PR |
| 01:00 | T+120 | answer key and scoring tool | scoring, to 01:20 |
| 01:30 | T+150 | none | retro filed on the drill issue |

### Heavy runs

Four drills share one machine tonight. A heavy run is any national `generate` or model run, or any production build. It takes `/tmp/pe-heavy.lock` (contents "pid label", created with noclobber, 22 GB free), and only inside this drill's own slots: 23:10–23:20 and 00:15–00:40.

Busy slots of other drills, in which this drill starts no heavy run:
- 21:40–22:05
- 22:15–22:35
- 22:45–23:10
- 23:20–23:45
- 23:50–00:10
- 00:55–01:20

A run that cannot finish inside its slot is not started. An overrun is logged, and the next slot owner logs the wait as lock wait. The model run (`heavy.py`) takes the lock itself and waits, without loading anything, while another job holds it.

## Gates

All commands run from the repository root unless stated.

- **G0, pair record (by 22:30, a comment on the drill PR).** Post:
  - the output of `make freeze DATASET=<file>` (that is, `uv run uk-energy-price-cap freeze --dataset <file>`): start SHA, clean tree, installed policyengine-uk and policyengine-core versions, `managed: false`, `certified: false`, the label, and the dataset build id and SHA-256. The record must show neither `dataset_problem` nor `engine_problem`;
  - the policyengine-uk and policyengine-core versions recorded in the build's release manifest on Hugging Face (the manifest files beside the h5 under `releases/microcosm-uk-2024-25-national/uk-frs-calibration-attempt-20261112T133744Z-6f918b81/` in `policyengine/populace-uk-private`), quoted with the manifest's path;
  - the pair-check result in one line: installed engine = the engine the manifest records = 2.177.7, and file SHA-256 = the build's. Otherwise, the mismatch;
  - the packet-guard line (13 hashes read), the lock state, and who holds each role.
- **G1, coverage ledger (23:00–23:10).** One ledger line per statement line, with a route and a cause class, `in_baseline_at_g1` set, and `coded` set. Post the ledger's commit SHA on the PR. Items already in the baseline are flagged here and not coded.
- **G2, provisional numbers (by 23:30).**
  1. Set `PLACEHOLDER_Q1_CAP` and the announced measures' values and status.
  2. Run `make generate DATASET=<file>` inside the 23:10–23:20 slot, or the placeholder `make generate` if a model run cannot finish in the slot.
  3. Then `make check`, and one hand-checked household per coded measure.
  4. Declare the basis once on the PR (below).
- **G3, re-base and reconcile (23:40–00:10).** Replace the single scaling in `household.py` with the published rates by payment method and fuel. Fill the reconciliation file (columns below): each gap over 10% gets a written reason and a gap class. Update ledger causes.
- **G5, correction (00:15–00:35).**
  1. Log the time the notice was read.
  2. If the page is wrong, withdraw the affected measures first.
  3. Fix the input in one commit and run `make generate DATASET=<file>` and `make check` inside the 00:15–00:40 slot.
  4. Re-run every hand-computed household row into its own file (never overwrite the G3 file).
  5. Re-check every ledger cause on the affected line itself, and record the new scoring SHA.
- **G4, publication path (by 00:40, inside the slot).**

  ```
  make check
  cd dashboard && NEXT_PUBLIC_MOCK=1 bun run build && bun run start -p 4873
  curl -sI http://localhost:4873/uk/energy-price-cap-jan-2027 | grep -i x-robots-tag
  curl -s http://localhost:4873/uk/energy-price-cap-jan-2027 | grep -o '<meta name="robots"[^>]*>'
  MOCK=1 ../scripts/smoke-built-site.sh http://localhost:4873/uk/energy-price-cap-jan-2027
  ```

  Stop the server by its PID and release the lock. Nothing is deployed.
- **Stop (00:50).** Log the stop commit. Nothing scored changes after it.

## Freeze at stop

By 00:55, and in any case before the key is released at 01:00, the integrator posts `FREEZE.txt` on the drill PR, then copies the frozen files to a folder outside the clone. `FREEZE.txt` holds the stop commit and the output of `shasum -a 256` over every scored file: the household scoring sheet, the ledger and the reconciliation. The scorer:
- scores only the frozen copies;
- checks each against `FREEZE.txt`;
- runs the released scoring tool on them.

The tool refuses any file whose SHA-256 differs from `FREEZE.txt`. A scored file that changes after the freeze is logged as a defect. It is never re-frozen, and the frozen copy is what is scored.

## Frozen file columns

Each file is CSV with one header row. Line ids are the statement's line ids; household ids are those in the household file.

- **Household scoring sheet:** the sheet released with the documents, one row per household: `household_id`, `scoring_sha`, `in_scope`, then the money columns it names, then `notes`.
- **Ledger:** `line`, `item`, `route`, `cause`, `in_baseline_at_g1` (yes or no, as posted at G1), `coded` (yes or no), `notes`.
- **Reconciliation:** `line`, `pe_figure`, `official`, `fiscal_year`, `basis`, `gap_class`, `reason`. A not-computable line leaves `pe_figure` empty or writes `n/a`, never 0.

## Roles

| Role | Owns | Does not |
|---|---|---|
| Drill owner | the sealed packet, releases at the set times, the answer key and the scoring tool | code, review or score |
| Integrator | the run branch, the drill PR, the clock table, every commit, generation, re-basing, G0 and `FREEZE.txt` | score households, or open any packet file before its release |
| Reconciler | the ledger, the reconciliation file, defects posted as PR comments within 5 minutes, the hash check of each release | push code |
| Scorer (the reconciler, after the documents) | the household scoring sheet, one commit SHA per scoring run, the hash check of the key and the scoring tool at 01:00, the score | edit reform code |

Who holds each role is recorded on the drill issue and in G0. One person per role; a combined role is recorded at G0 as a deviation.

## Routes and cause classes

Every ledger line gets one route:

| Route | Where the work lands | Meaning |
|---|---|---|
| `dashboard-param` | this repo | a parameter change |
| `dashboard-structural` | this repo | a new modifier or variable |
| `needs-pe-uk-first` | policyengine-uk | the engine has no route; a draft is filed the same day and linked |
| `not-computable` | data (Microcosm) | the input is not in the data or the model; shown with the reason, never as £0 |
| `ledger` | none | not modelled; the official figure is recorded |

Every ledger line also gets one **cause class**: what the measure needs before PolicyEngine can show it.
- `parameter`: an existing parameter carries it.
- `formula`: engine or modifier logic must change.
- `coverage`: the input the measure acts on is not in the data or the model. This applies to every not-computable line.
- `baseline_mismatch`: the baseline already holds the measure, or holds a different value from the official baseline. This applies to every item already in the baseline.
- `timing_fiscal_calendar`: the start date, part year or fiscal-year placement is the substance.
- `interaction`: the measure works through another benefit or measure.
- `data_calibration`: the data hold the input but its level is off.
- `basis`: a presentation choice only.

Every reconciliation row over 10% gets one **gap class**: why our figure differs from the official one by more than 10%.
- `basis`: static against behavioural, accrued against cash, geography, price base, or gross against net.
- `data_calibration`: the data's count or level of the affected group differs from the official one for the same year.
- `baseline_mismatch`: the official baseline holds different policy or forecast assumptions.
- `timing_fiscal_calendar`.
- `coverage`.
- `interaction`.

The cause class and the gap class are separate columns. Where a line has equal values in both, it needs a written reason.

## Basis, declared once on the PR at G2

State each of these once, and hold it:
- annual or quarterly;
- fiscal or calendar year;
- gross or net of support;
- static or behavioural;
- the typical-consumption basis of any cap level or ratio (issue #3);
- country coverage, and whether Northern Ireland is in or out.

## Household rounding

Household values are computed in decimal arithmetic (for example Python's `decimal` with `ROUND_HALF_UP`), never in binary floating point. Each reported figure is computed from unrounded components and rounded once, at the end, to the penny, half up. `round()` on a float does not round half up, and a binary float cannot hold most half-penny values exactly. The documents state the exact basis for the example households.

## Rubric (100 points)

| Part | Points | How it is scored |
|---|---|---|
| Households | 20 | each value exact to the penny (decimal arithmetic, half up, once), on the values in force after the correction; 20 × exact / cells |
| National | 30 | per statement line: basis (half) and gap class (half). For not-computable and ledger lines, the basis column carries the costing's basis, and the gap point is for recording the costing and the reason no figure is shown |
| Ledger | 25 | per line, route and cause class at the frozen stop state; items already in the baseline score only if flagged as such at G1 and left uncoded |
| Publication | 10 | MOCK banner on every view, noindex meta and `X-Robots-Tag` on `next start`, not-computable lines shown with reasons and never as £0, disclosure floor, every coded measure on the page |
| Process | 15 | G0 pair record posted on the drill PR by 22:30 (3); gates on time (4); one commit SHA per scoring run (3); correction logged and every hand row re-run into its own file (2); `FREEZE.txt` with the SHA-256 of every scored file posted before 01:00, and nothing scored changed after it (3) |

The key states its per-row weights. Households, national and ledger are scored by the released scoring tool on the frozen files. Publication and process are scored by hand from the clock table and the G4 record.

## What to time and log

The integrator keeps the clock table on the drill PR. Each step gets its start, end, machine minutes, people minutes and SHA:

| Step | Planned | Start | End | Machine min | People min | SHA |
|---|---|---|---|---|---|---|
| G0 | 22:30 | | | | | |
| G1 | 23:10 | | | | | |
| G2 | 23:30 | | | | | |
| Documents received | 23:40 | | | | | |
| G3 | 00:10 | | | | | |
| Correction received | 00:15 | | | | | |
| G5 | 00:35 | | | | | |
| G4 | 00:40 | | | | | |
| Stop | 00:50 | | | | | |
| `FREEZE.txt` posted | 00:55 | | | | | |

Also log:
- the time each release arrived and its hash check;
- every scoring run, with one commit SHA each;
- the time the correction was read, the time the re-run finished, and the new scoring SHA;
- every defect, as a PR comment with the time found, read and fixed;
- every upstream draft filed (repository, link, time);
- every heavy run: start, end, peak memory and lock wait.

## MOCK and noindex rules

- Every view of the drill build shows a banner that starts with **MOCK** (built with `NEXT_PUBLIC_MOCK=1`). The template's pre-release banner is not enough.
- The served HTML carries a robots meta with `noindex` and `nofollow`, and every response carries `X-Robots-Tag: noindex, nofollow`. Check both on `next start`, not on a dev server.
- `make check` (both public-data checks and the manifest) passes on the stop commit. Registry measures keep their `placeholder` flag.
- Nothing is deployed: no preview URL, Vercel, Modal or Cloud Run.
- Mock figures never appear in this repository, its issues or its PRs. The drill PR records process only: gates, times, SHAs, classes and the score by part.

## Packet hygiene

- The packet is written and held outside this repository. Only the hashes below are committed.
- Files are released at the set times, never early, into `~/drill11-released/` (outside the clone). The release post on the drill issue names the file, its hash and the time, never its contents.
- The reconciler checks each release's SHA-256 on arrival (`shasum -a 256 <file>`) against the table below and logs the result. The scorer does the same for the key and the scoring tool at 01:00.
- The integrator opens no packet file before its release time.
- Ledgers, reconciliation and scoring sheets are kept outside the clone or never pushed, and are not posted. Only their hashes go in `FREEZE.txt`.
- CI on the drill branch fails if any tracked file has the SHA-256 of a packet file (`scripts/check_packet_not_committed.py`).

## Packet hashes (SHA-256)

| File | Released at | SHA-256 |
|---|---|---|
| `00-owner-notes.md` | never (drill owner only) | `a899c8eef2919c42289febf50b672c7a511afb675215656aa71bff2cc8b07d2d` |
| `01-statement.md` | 23:00 | `77c0ba55051cd1a7ee5e7dda569647aef66a7c7ce9966418d5f6728d174d858b` |
| `02-documents.md` | 23:40 | `50663d7c02c8b28d49df3c31f3ca86afa96b7e14939a6cbfa0a03c974f60b94d` |
| `02-costings.csv` | 23:40 | `f90be7eb485922aa11b24582052ff6400abbcedb9281a0a303df3915b5832900` |
| `02-households.csv` | 23:40 | `db5893c315c3296ead28c25ffe81404288c708c5bfd27b602e6af80c7e741719` |
| `02-scoring-sheet.csv` | 23:40 | `125a1fcd1e6494bb5543b339528c8361f122fa6639ac4133534fd8bca9061851` |
| `03-correction.md` | 00:15 | `280ddf151ffe757d39f12bf25d6eb9c45711a3a08fae355c08487a759412a698` |
| `04-answer-key.md` | 01:00 | `9c34f7f5cb90f54693baca2bf6e4b116b5116792f31344beb5c8deaaeaa30ac6` |
| `04-answer-key-households.csv` | 01:00 | `c612f378c5b8668f7cd71148e66511a30502d39712e1584b9a769eba8fe8c271` |
| `04-answer-key-ledger.csv` | 01:00 | `b8dcb7de0af01139df67c4a2a9c0cd09cba93dcbae1b2a3494dc7404851b7bd3` |
| `generate_household_key.py` | 01:00 | `9266f9b01a1eb2fa94bdaceedfda77b9460272eefecea19044c3d9d8b378c77b` |
| `04-score.py` | 01:00 | `74666fedbcbe25c91942ee068117727025f1e2f6e35d7f89f4a99e1fb46e1f36` |

Check with `shasum -a 256 <file>`.
