"""Fail if any tracked file is a drill packet file.

The drill plan (root DRILL.md on a drill branch) lists the SHA-256 of each
packet file. This hashes every file git tracks and fails on a match, so a
released file copied into the clone cannot be committed by accident. With
no DRILL.md (this branch, or main), there is nothing to check.

    uv run python scripts/check_packet_not_committed.py [DRILL.md]
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIGEST = re.compile(r"\b[0-9a-f]{64}\b")


def packet_hashes(plan: Path) -> set[str]:
    return set(DIGEST.findall(plan.read_text())) if plan.exists() else set()


def tracked_files(root: Path = ROOT) -> list[Path]:
    out = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    ).stdout.decode()
    return [root / name for name in out.split("\0") if name]


def check(plan: Path, files: list[Path]) -> list[str]:
    hashes = packet_hashes(plan)
    if not hashes:
        return []
    problems = []
    for path in files:
        if not path.is_file() or path.resolve() == plan.resolve():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:
            problems.append(f"{path.relative_to(ROOT)}: a drill packet file")
    return problems


if __name__ == "__main__":
    plan = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "DRILL.md"
    found = check(plan, tracked_files())
    for problem in found:
        print(problem, file=sys.stderr)
    print(f"{len(found)} packet file(s) tracked")
    sys.exit(1 if found else 0)
