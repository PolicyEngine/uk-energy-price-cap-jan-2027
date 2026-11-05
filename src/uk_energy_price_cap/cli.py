"""Command line: generate results, print the ledger, validate a file."""

import argparse
import csv
import json
import sys
from pathlib import Path

from uk_energy_price_cap import pipeline, publication, reforms

DEFAULT_OUT = Path("dashboard/public/data/results.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="uk-energy-price-cap")
    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="write results.json")
    gen.add_argument("--out", type=Path, default=DEFAULT_OUT)
    gen.add_argument(
        "--source", choices=["placeholder", "model"], default="placeholder"
    )
    sub.add_parser("ledger", help="print the coverage ledger as CSV")
    val = sub.add_parser("validate", help="check a results file")
    val.add_argument("path", type=Path, nargs="?", default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    if args.command == "generate":
        pipeline.generate(args.out, args.source)
        print(f"wrote {args.out} ({publication.sha256(args.out)[:12]})")
        return 0
    if args.command == "ledger":
        rows = reforms.ledger_rows()
        writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return 0
    problems = publication.validate(json.loads(args.path.read_text()))
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
