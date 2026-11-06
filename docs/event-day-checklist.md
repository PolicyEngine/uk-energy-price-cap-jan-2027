# Event-day checklist (one page)

Detail for each step is in [RUNBOOK.md](RUNBOOK.md). Tick in the PR, with the time.

| When | Step | Command | Done when |
|---|---|---|---|
| T−60 | G0 freeze | `make freeze DATASET=<file>` | record posted in the PR |
| T | Read Ofgem's release and any government statement | – | – |
| T to T+10 | G1 ledger | `make ledger` | one line per item, route and cause set; baseline items marked |
| T+30 | G2 provisional | set `PLACEHOLDER_Q1_CAP`, statuses; `make generate` | typical bill within £1 of Ofgem; one hand check per measure |
| T+40 to T+70 | G3 re-base | Annex 9 rates into `household.py`; `make generate check` | every gap over 10% has a reason; ledger causes updated |
| any time | G5 correction | withdraw, fix, `make generate check` | new results SHA logged; hand checks re-run |
| before publishing | G4 check | `make build`, `bun run start`, `curl -sI` | banner, `noindex`, checks clean, two people agree |
| publishing | G4 go public | one commit (RUNBOOK G4 list) | page and tests agree |
| if wrong after publishing | rollback | `git revert -m 1 <merge>` | previous page back |
