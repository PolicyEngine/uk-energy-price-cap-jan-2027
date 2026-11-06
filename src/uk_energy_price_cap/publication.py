"""Publication gate (scaled down): disclosure floor, validation, manifest.

The figures come from survey microdata licensed through the UK Data
Service, and this repository is public. A public file must never carry
record identifiers or weights, and every cell must rest on at least
``DISCLOSURE_FLOOR`` survey households or be withheld (value ``None``,
``withheld: true``).
"""

import hashlib
import json
import re
from pathlib import Path

from uk_energy_price_cap import reforms, sign_off

DISCLOSURE_FLOOR = 10

FORBIDDEN_KEYS = re.compile(
    r"(^|_)(household_id|person_id|benunit_id|weight|weights|record_id|"
    r"sernum|records|n_records|sample_size)$"
)
# ONS area codes (constituency, local authority and others).
AREA_CODE = re.compile(r"\b[ENSWK]\d{8}\b")


class PublicationError(ValueError):
    """A results file failed the publication gate."""


def apply_floor(value: float | None, records: int) -> float | None:
    """The value, or None when it rests on too few survey households."""
    if records < DISCLOSURE_FLOOR:
        return None
    return value


def _walk(node, path="$"):
    if isinstance(node, dict):
        for key, value in node.items():
            yield path, key, value
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, f"{path}[{index}]")


def validate(results: dict) -> list[str]:
    """Problems with a results file; an empty list means it may be public."""
    problems = []
    for path, key, value in _walk(results):
        if FORBIDDEN_KEYS.search(str(key)):
            problems.append(f"{path}.{key}: identifiers, weights or counts")
        if isinstance(value, str) and AREA_CODE.search(value):
            problems.append(f"{path}.{key}: area code in a value")
        if isinstance(value, dict) and value.get("withheld") is True:
            numeric = [
                k
                for k, v in value.items()
                if k != "withheld"
                and isinstance(v, (int, float))
                and not isinstance(v, bool)
            ]
            if numeric:
                problems.append(f"{path}.{key}: withheld cell has values")

    meta = results.get("meta", {})
    ids = [m["id"] for m in results.get("measures", [])]
    if sorted(ids) != sorted(r.id for r in reforms.REFORMS):
        problems.append("measures: list differs from the registry")
    placeholders = [
        m["id"]
        for m in results.get("measures", [])
        if m.get("status") not in ("announced", "withdrawn")
    ]
    if placeholders and meta.get("placeholder") is not True:
        problems.append(
            "meta.placeholder must be true while measures are placeholders: "
            + ", ".join(placeholders)
        )
    if sign_off.REQUIRED and meta.get("placeholder") is not True:
        problems.append(
            "sign_off.REQUIRED is on: only a placeholder file may be written"
        )
    for m in results.get("measures", []):
        if not m.get("computable") and m.get("cost_gbp_m") is not None:
            problems.append(
                f"measures.{m['id']}: not computable but carries a cost"
            )
        if m.get("computable") is False and not m.get("reason"):
            problems.append(f"measures.{m['id']}: not computable, no reason")
        if m.get("status") == "withdrawn" and m.get("cost_gbp_m") is not None:
            problems.append(
                f"measures.{m['id']}: withdrawn but carries a cost"
            )
    return problems


def check(results: dict) -> None:
    problems = validate(results)
    if problems:
        raise PublicationError("\n".join(problems))


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


MANIFEST_NAME = "manifest.json"


def _git(*args: str) -> str | None:
    import subprocess

    try:
        out = subprocess.run(
            ["git", *args],
            cwd=Path(__file__).resolve().parent,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip()


def git_state() -> dict:
    """HEAD and whether the tracked tree is clean (untracked files ignored)."""
    head = _git("rev-parse", "HEAD")
    status = _git("status", "--porcelain", "--untracked-files=no")
    return {"commit": head, "clean": status == ""}


def installed_versions() -> dict:
    """Versions read from the installed packages, not from constants."""
    from importlib import metadata

    out = {}
    for name in ("policyengine", "policyengine-uk", "policyengine-core"):
        try:
            out[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name] = None
    return out


def manifest(results_path: Path, results: dict, run: dict | None = None):
    """Receipt for one generation: the results digest and what made it.

    A placeholder generation records only what is fixed by the code (so the
    committed file is reproducible); a model run adds the commit, the
    clean-tree flag, installed versions and the dataset (``run``).
    """
    meta = results.get("meta", {})
    out = {
        "results": {
            "path": Path(results_path).name,
            "sha256": sha256(results_path),
        },
        "source": meta.get("source"),
        "placeholder": meta.get("placeholder"),
        "engine": meta.get("engine"),
    }
    if run:
        out["run"] = run
    return out


def write_manifest(results_path: Path, results: dict, run=None) -> Path:
    path = Path(results_path).with_name(MANIFEST_NAME)
    if run is None:
        run = results.get("meta", {}).get("run")
    write_json(path, manifest(results_path, results, run))
    return path


def check_manifest(results_path: Path) -> list[str]:
    """Problems with the manifest beside a results file."""
    path = Path(results_path).with_name(MANIFEST_NAME)
    if not path.exists():
        return [f"{path.name}: missing"]
    data = json.loads(path.read_text())
    problems = []
    if data.get("results", {}).get("sha256") != sha256(results_path):
        problems.append(f"{path.name}: results SHA-256 does not match")
    if data.get("source") == "model":
        run = data.get("run") or {}
        for key in ("commit", "clean", "versions", "dataset"):
            if key not in run:
                problems.append(f"{path.name}: model run without {key}")
        if run.get("clean") is False:
            problems.append(f"{path.name}: model run on a dirty tree")
    return problems


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
