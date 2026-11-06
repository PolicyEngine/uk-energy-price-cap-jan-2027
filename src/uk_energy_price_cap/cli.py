"""Command line: freeze, generate results, print the ledger, validate."""

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
    frz = sub.add_parser(
        "freeze",
        help="print the G0 freeze record (versions, dataset SHA); fails without the dataset",
    )
    frz.add_argument("--dataset", type=Path, default=None)
    gen = sub.add_parser("generate", help="write results.json and manifest")
    gen.add_argument("--out", type=Path, default=DEFAULT_OUT)
    gen.add_argument(
        "--source", choices=["placeholder", "model"], default="placeholder"
    )
    gen.add_argument("--dataset", type=Path, default=None)
    gen.add_argument(
        "--allow-unmanaged",
        action="store_true",
        help='run on an uncertified pair; figures are labelled "unvalidated"',
    )
    sub.add_parser("ledger", help="print the coverage ledger as CSV")
    val = sub.add_parser("validate", help="check a results file and manifest")
    val.add_argument("path", type=Path, nargs="?", default=DEFAULT_OUT)
    args = parser.parse_args(argv)

    if args.command == "freeze":
        from uk_energy_price_cap import model_run

        if args.dataset is None:
            print(
                "Name the frozen dataset file with --dataset.", file=sys.stderr
            )
            return 1
        path = args.dataset.expanduser()
        if not path.is_file():
            print(f"{path}: no such dataset file", file=sys.stderr)
            return 1
        print(json.dumps(model_run.freeze_record(path), indent=2))
        return 0
    if args.command == "generate":
        pipeline.generate(
            args.out, args.source, args.dataset, args.allow_unmanaged
        )
        print(f"wrote {args.out} ({publication.sha256(args.out)[:12]})")
        return 0
    if args.command == "ledger":
        rows = reforms.ledger_rows()
        writer = csv.DictWriter(sys.stdout, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        return 0
    problems = publication.validate(json.loads(args.path.read_text()))
    problems += publication.check_manifest(args.path)
    for problem in problems:
        print(problem, file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
