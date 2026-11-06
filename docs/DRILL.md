# Drill

The drill plan for Friday 13 November 2026 (clock, roles, rubric and packet hashes) has one home: `DRILL.md` on the `drill-plan` branch, PR #12: https://github.com/PolicyEngine/uk-energy-price-cap-jan-2027/blob/drill-plan/DRILL.md. This file is a pointer only and carries no hashes.

A drill branch cut from this branch or from `main` does not carry the plan. Its first commit brings it in:

```
git checkout origin/drill-plan -- DRILL.md
git commit -m "Bring the drill plan onto the drill branch"
uv run python scripts/check_packet_not_committed.py   # must report 8 packet hashes read
```

On any branch whose name contains `drill`, `scripts/check_packet_not_committed.py` fails if the root `DRILL.md` is missing or lists no hashes, so CI does not pass without checking anything.
