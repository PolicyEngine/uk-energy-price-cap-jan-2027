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
        if m.get("status") != "announced"
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
    return problems


def check(results: dict) -> None:
    problems = validate(results)
    if problems:
        raise PublicationError("\n".join(problems))


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def manifest(results_path: Path, inputs: dict[str, str]) -> dict:
    """Receipt for one generation: the results digest and what made it."""
    return {
        "results": {"path": str(results_path), "sha256": sha256(results_path)},
        "inputs": dict(sorted(inputs.items())),
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
