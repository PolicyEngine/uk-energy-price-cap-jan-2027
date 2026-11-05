"""Parameter-change templates (scaled down from the Autumn Budget 2026 set).

A measure built only from these templates needs no attestation: each one
returns a plain ``{path: {period: value}}`` mapping and refuses a path the
engine cannot represent. Hand-written modifiers go in ``measures/``, one
module per modifier, with literal defaults and no runtime state.
"""

from decimal import Decimal
from math import isfinite
from typing import Any, Mapping

from uk_energy_price_cap.data_limits import warn_if_data_limited
from uk_energy_price_cap.model_limits import model_limit_reason

QUARTER_STARTS = {"Q1": "01-01", "Q2": "04-01", "Q3": "07-01", "Q4": "10-01"}


class TemplateError(ValueError):
    """A template was given a value or path it cannot use."""


def _check_path(path: str) -> None:
    if not path.startswith("gov."):
        raise TemplateError(f"{path}: not a parameter path")
    reason = model_limit_reason(path)
    if reason:
        raise TemplateError(f"{path}: {reason}")
    warn_if_data_limited(path)


def _finite(value: Any, label: str) -> float:
    try:
        number = float(Decimal(str(value)))
    except Exception as error:  # noqa: BLE001
        raise TemplateError(f"{label}: {value!r} is not a number") from error
    if not isfinite(number):
        raise TemplateError(f"{label}: {value!r} is not finite")
    return number


def _period(key: Any) -> str:
    """2027 -> '2027-01-01'; '2027-04-06' stays as it is."""
    text = str(key)
    if text.isdigit() and len(text) == 4:
        return f"{text}-01-01"
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        return text
    raise TemplateError(f"{key!r}: use a year or a YYYY-MM-DD date")


def amount_change(
    path: str, values: Mapping[Any, Any]
) -> dict[str, dict[str, float]]:
    """A cash amount from each date (e.g. a payment of £200 from 2027-01-01)."""
    _check_path(path)
    out = {}
    for key, value in values.items():
        amount = _finite(value, path)
        if amount < 0:
            raise TemplateError(f"{path}: an amount cannot be negative")
        out[_period(key)] = amount
    return {path: out}


def rate_change(
    path: str, values: Mapping[Any, Any]
) -> dict[str, dict[str, float]]:
    """A rate between 0 and 1 from each date (e.g. a VAT rate of 0)."""
    _check_path(path)
    out = {}
    for key, value in values.items():
        rate = _finite(value, path)
        if not 0 <= rate <= 1:
            raise TemplateError(f"{path}: a rate must lie in [0, 1]")
        out[_period(key)] = rate
    return {path: out}


def list_change(
    path: str, values: Mapping[Any, list[str]]
) -> dict[str, dict[str, list[str]]]:
    """A list-valued parameter (council tax bands, countries, benefits)."""
    _check_path(path)
    out = {}
    for key, value in values.items():
        if not isinstance(value, list) or not value:
            raise TemplateError(f"{path}: give a non-empty list")
        if len(set(value)) != len(value):
            raise TemplateError(f"{path}: the list repeats an item")
        out[_period(key)] = list(value)
    return {path: out}


def quarterly_growth_change(
    path: str, values: Mapping[str, Any]
) -> dict[str, dict[str, float]]:
    """Quarter-on-quarter growth, keyed '2027Q1', as a fraction (0.26)."""
    _check_path(path)
    out = {}
    for key, value in values.items():
        text = str(key)
        if len(text) != 6 or text[4] != "Q" or text[4:] not in QUARTER_STARTS:
            raise TemplateError(f"{key!r}: use a quarter such as 2027Q1")
        growth = _finite(value, path)
        if not -0.9 < growth < 2:
            raise TemplateError(f"{path}: growth {growth} is out of range")
        out[f"{text[:4]}-{QUARTER_STARTS[text[4:]]}"] = growth
    return {path: out}


def growth_for_cap(new_cap: float, previous_cap: float) -> float:
    """Growth that takes a typical bill from ``previous_cap`` to ``new_cap``.

    Both caps must be on the same typical-consumption basis (issue #3).
    """
    new = _finite(new_cap, "new_cap")
    previous = _finite(previous_cap, "previous_cap")
    if previous <= 0 or new <= 0:
        raise TemplateError("caps must be positive")
    return round(new / previous - 1, 6)


def merge(*changes: Mapping[str, Mapping]) -> dict[str, dict]:
    """Combine template outputs; the same path and period twice is an error."""
    merged: dict[str, dict] = {}
    for change in changes:
        for path, periods in change.items():
            target = merged.setdefault(path, {})
            for period, value in periods.items():
                if period in target:
                    raise TemplateError(f"{path} {period}: set twice")
                target[period] = value
    return merged


TEMPLATES = {
    "amount_change": amount_change,
    "rate_change": rate_change,
    "list_change": list_change,
    "quarterly_growth_change": quarterly_growth_change,
}
