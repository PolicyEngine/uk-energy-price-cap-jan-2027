"""Ofgem cap levels, scenarios and bill arithmetic (no model needed).

Levels and rates come from ``cap_levels.json``. The 2027Q1 scenarios are
placeholders until Ofgem announces the cap. Every ratio taken here uses
levels on the same typical-consumption basis: the July 2026 change of
basis (2,700/11,500 kWh to 2,500/9,500 kWh) is never read as a price
change (issue #3).
"""

import json
from decimal import ROUND_HALF_UP, Decimal
from importlib import resources

CAP = json.loads(
    resources.files(__package__).joinpath("cap_levels.json").read_text()
)

CURRENT_PERIOD = "2026Q4"
CURRENT_BASIS = "2026"
DAYS = 365
# Shares of a year's domestic consumption used in January to March
# (policyengine-uk 2.177.7 energy_prices/consumption_shares.yaml, DESNZ
# Energy Trends, mean of 2015 to 2025): the change over the quarter alone.
Q1_CONSUMPTION_SHARE = {"electricity": 0.2929, "gas": 0.4250}


def pence_to_pounds(value: float) -> float:
    """Round to the penny, half up, as on a bill."""
    return float(
        Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def current_rates() -> dict:
    return CAP["gb_average_direct_debit_rates"][CURRENT_PERIOD]


def scenario(scenario_id: str) -> dict:
    for row in CAP["scenarios_2027q1"]:
        if row["id"] == scenario_id:
            return row
    raise KeyError(scenario_id)


def scenario_ids() -> list[str]:
    return [row["id"] for row in CAP["scenarios_2027q1"]]


def current_cap() -> int:
    return CAP["payment_methods"][CURRENT_PERIOD]["direct_debit"]


def price_factor(scenario_id: str) -> float:
    """Ratio of the scenario cap to the October to December 2026 cap.

    Both are on the 2026 typical-consumption basis. Placeholder: on the day
    the factor comes from Ofgem's rates by fuel (Annex 9), not one ratio.
    """
    return scenario(scenario_id)["direct_debit"] / current_cap()


def annual_bill(
    electricity_kwh: float,
    gas_kwh: float,
    rates: dict | None = None,
) -> dict[str, float]:
    """Annual dual-fuel bill (VAT included) from kWh and unit/standing rates.

    A home with no gas (``gas_kwh == 0``) pays no gas standing charge.
    """
    rates = rates or current_rates()
    if electricity_kwh < 0 or gas_kwh < 0:
        raise ValueError("kWh cannot be negative")
    electricity = (
        electricity_kwh * rates["electricity_unit_p_per_kwh"]
        + DAYS * rates["electricity_standing_p_per_day"]
    ) / 100
    gas = 0.0
    if gas_kwh > 0:
        gas = (
            gas_kwh * rates["gas_unit_p_per_kwh"]
            + DAYS * rates["gas_standing_p_per_day"]
        ) / 100
    return {
        "electricity": pence_to_pounds(electricity),
        "gas": pence_to_pounds(gas),
        "total": pence_to_pounds(electricity + gas),
    }


def scaled_rates(factor: float, rates: dict | None = None) -> dict:
    """All unit rates and standing charges scaled by one factor (placeholder)."""
    rates = dict(rates or current_rates())
    for key in (
        "electricity_unit_p_per_kwh",
        "electricity_standing_p_per_day",
        "gas_unit_p_per_kwh",
        "gas_standing_p_per_day",
    ):
        rates[key] = rates[key] * factor
    return rates


def consistent_history() -> list[dict]:
    """Cap history with the basis on every row; restated rows flagged."""
    return [dict(row) for row in CAP["history"]]
