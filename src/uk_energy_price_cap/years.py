"""Base year, policy years and the declared basis (one place)."""

import json
from importlib import resources

_DATA = json.loads(
    resources.files(__package__).joinpath("years.json").read_text()
)

BASE_YEAR: int = _DATA["base_year"]
POLICY_YEARS: tuple[int, ...] = tuple(_DATA["policy_years"])
EVENT_QUARTER: str = _DATA["event_quarter"]
BASIS: dict[str, str] = dict(_DATA["basis"])


def fiscal_label(year: int) -> str:
    """Model year 2026 -> '2026-27'."""
    return f"{year}-{(year + 1) % 100:02d}"
