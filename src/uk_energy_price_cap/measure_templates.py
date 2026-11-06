"""Parameter-change templates (scaled down from the Autumn Budget 2026 set).

A measure built only from these templates needs no attestation: each one
returns a plain ``{path: {period: value}}`` mapping and refuses a path the
engine cannot represent. Hand-written modifiers go in ``measures/``, one
module per modifier, with literal defaults and no runtime state.
"""

import re
from datetime import date
from decimal import Decimal
from math import isfinite
from typing import Any, Mapping

from uk_energy_price_cap.data_limits import warn_if_data_limited
from uk_energy_price_cap.model_limits import model_limit_reason

QUARTERS = {
    "Q1": ("01-01", "03-31"),
    "Q2": ("04-01", "06-30"),
    "Q3": ("07-01", "09-30"),
    "Q4": ("10-01", "12-31"),
}
# [0-9], not \d: \d also matches other scripts' digits.
BARE_YEAR = re.compile(r"[1-9][0-9]{3}")


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


def _date(text: str) -> date:
    try:
        return date.fromisoformat(text)
    except ValueError as error:
        raise TemplateError(f"{text!r}: not a YYYY-MM-DD date") from error


def _period(key: Any) -> str:
    """A bare fiscal year, or a ``start.stop`` interval for a part year.

    policyengine-uk reads a bare year (``"2026"``) as that fiscal year and
    ``"2027-07-01.2028-03-31"`` as that interval
    (``policyengine_uk.utils.dated_reforms``). A lone date changes one day
    of the parameter and leaves the year it was meant for untouched, so it
    is refused (Autumn Budget 2026, tests/test_measure_keys.py).
    """
    text = str(key)
    if BARE_YEAR.fullmatch(text):
        return text
    if "." in text:
        start, stop = text.split(".", 1)
        if _date(start) >= _date(stop):
            raise TemplateError(f"{key!r}: the interval ends before it starts")
        return text
    raise TemplateError(
        f"{key!r}: use a fiscal year such as 2026 or an interval such as "
        "2027-07-01.2028-03-31; a lone date changes one day"
    )


def amount_change(
    path: str, values: Mapping[Any, Any]
) -> dict[str, dict[str, float]]:
    """A cash amount for each fiscal year or interval (e.g. £200 in 2026)."""
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
    """A rate between 0 and 1 for each fiscal year or interval."""
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
    """Year-on-year growth for single calendar quarters, keyed '2027Q1'.

    For ``gov.economic_assumptions.energy_prices.obr.utilities``: the OBR's
    CPI utilities inflation, year on year, by calendar quarter. The index
    builder sets each quarter's level to the level a year earlier times
    ``1 + g`` (with the electricity VAT change taken out), so a change to
    one quarter's rate also moves the same quarter a year later unless that
    rate is offset too (``cap_shock``). Each key becomes that quarter's
    interval, so no other quarter of the year moves.
    """
    _check_path(path)
    out = {}
    for key, value in values.items():
        text = str(key)
        if (
            len(text) != 6
            or not BARE_YEAR.fullmatch(text[:4])
            or text[4:] not in QUARTERS
        ):
            raise TemplateError(f"{key!r}: use a quarter such as 2027Q1")
        growth = _finite(value, path)
        if not -0.9 < growth < 2:
            raise TemplateError(f"{path}: growth {growth} is out of range")
        start, stop = QUARTERS[text[4:]]
        out[f"{text[:4]}-{start}.{text[:4]}-{stop}"] = growth
    return {path: out}


def cap_shock(
    new_cap: float,
    forecast_cap: float,
    forecast_growth: float,
    forecast_growth_next_year: float,
) -> tuple[float, float]:
    """Growth rates that move one quarter from the forecast path to a cap.

    ``forecast_cap`` is the typical bill the OBR's path implies for the
    quarter, and ``forecast_growth`` the OBR's year-on-year rate for it;
    ``forecast_growth_next_year`` is the rate for the same quarter a year
    later. Returns ``(g, g_next)``: ``g`` makes the quarter's index level
    ``new_cap / forecast_cap`` times the baseline level; ``g_next`` brings
    the same quarter a year later back to the baseline level, so the gap
    lasts one quarter. Both caps must be on the same typical-consumption
    basis (issue #3). The VAT adjustment the builder applies is the same
    in baseline and reform, so it cancels in the ratio.
    """
    new = _finite(new_cap, "new_cap")
    forecast = _finite(forecast_cap, "forecast_cap")
    if forecast <= 0 or new <= 0:
        raise TemplateError("caps must be positive")
    ratio = new / forecast
    g = (1 + _finite(forecast_growth, "forecast_growth")) * ratio - 1
    g_next = (
        1 + _finite(forecast_growth_next_year, "forecast_growth_next_year")
    ) / ratio - 1
    return round(g, 6), round(g_next, 6)


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
