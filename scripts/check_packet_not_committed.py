"""Fail if any tracked file is a drill packet file.

The drill plan (root DRILL.md, brought onto the drill branch from the
`drill-plan` branch) lists the SHA-256 of each packet file. This hashes
every file git tracks and fails on a match, so a released file copied into
the clone cannot be committed by accident.

On a branch whose name contains "drill" (GITHUB_HEAD_REF, then
GITHUB_REF_NAME, then the local branch), a missing root DRILL.md, or one
with no hashes, is itself a failure: the guard would otherwise pass without
checking anything. On other branches (this template, or main), there is no
plan and nothing to check.

    uv run python scripts/check_packet_not_committed.py [DRILL.md]
"""

import hashlib
import os
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


def branch_name(env=os.environ, root: Path = ROOT) -> str:
    for key in ("GITHUB_HEAD_REF", "GITHUB_REF_NAME"):
        if env.get(key):
            return env[key]
    out = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=root,
        capture_output=True,
    )
    return out.stdout.decode().strip() if out.returncode == 0 else ""


def is_drill_branch(name: str) -> bool:
    return "drill" in name.lower()


def check(
    plan: Path, files: list[Path], drill_branch: bool = False
) -> list[str]:
    hashes = packet_hashes(plan)
    if not hashes:
        if drill_branch:
            return [
                f"{plan.name}: no packet hashes found on a drill branch; "
                "run `git checkout origin/drill-plan -- DRILL.md` and commit it"
            ]
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
    branch = branch_name()
    drill = is_drill_branch(branch)
    found = check(plan, tracked_files(), drill_branch=drill)
    for problem in found:
        print(problem, file=sys.stderr)
    print(
        f"branch {branch or '(none)'}: {len(packet_hashes(plan))} packet hash(es) "
        f"read, {len(found)} problem(s)"
    )
    sys.exit(1 if found else 0)
