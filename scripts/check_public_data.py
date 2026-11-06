"""Check every file the dashboard serves before it can be published.

Non-negotiable: this repository is public and the figures come from
UKDS-licensed microdata. Fails on record identifiers, weights or counts,
area codes, withheld cells that still carry values, microdata files, and a
results file that fails ``publication.validate``.

    uv run python scripts/check_public_data.py
"""

import json
import sys
from pathlib import Path

from uk_energy_price_cap import publication

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "dashboard" / "public"
BANNED_SUFFIXES = {
    ".h5",
    ".h5ad",
    ".parquet",
    ".feather",
    ".pkl",
    ".sav",
    ".dta",
}


TEXT_SUFFIXES = {".json", ".csv", ".txt", ".md", ".svg", ".html"}


def check(public: Path = PUBLIC) -> list[str]:
    problems = []
    for path in sorted(public.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(public)
        if path.suffix.lower() in BANNED_SUFFIXES:
            problems.append(f"{rel}: microdata file type")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text()
        # Area codes in any public text file, as the JS checker does.
        if publication.AREA_CODE.search(text):
            problems.append(f"{rel}: area code")
        if path.suffix == ".json":
            data = json.loads(text) if text.strip() else None
            if data is None:
                problems.append(f"{rel}: empty JSON file")
            elif rel.name == "results.json":
                problems += [f"{rel}: {p}" for p in publication.validate(data)]
            else:
                for where, key, value in publication._walk(data):
                    if publication.FORBIDDEN_KEYS.search(str(key)):
                        problems.append(f"{rel} {where}.{key}: forbidden key")
        if path.suffix == ".csv":
            lines = text.splitlines()
            header = lines[0].split(",") if lines else []
            for column in header:
                if publication.FORBIDDEN_KEYS.search(column.strip()):
                    problems.append(f"{rel}: forbidden column {column}")
    return problems


if __name__ == "__main__":
    found = check()
    for problem in found:
        print(problem, file=sys.stderr)
    print(f"{len(found)} problem(s)")
    sys.exit(1 if found else 0)
