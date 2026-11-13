"""What the engine cannot represent yet, and what needs a newer engine.

``MODEL_LIMITS`` names levers with no parameter or variable in
policyengine-uk. ``MIN_ENGINE`` names parameters that exist only from a
given policyengine-uk version. The model run uses policyengine-uk 2.177.7
(``data_build.DATA_BUILD``), which has all of them (issue #1).
"""

import warnings


class ModelLimitedWarning(UserWarning):
    """A reform needs something the engine does not have."""


MODEL_LIMITS: dict[str, str] = {
    "gov.hmrc.vat.domestic_gas_rate": (
        "No VAT rate of its own for domestic gas: gas reads "
        "gov.hmrc.vat.reduced_rate, which every reduced-rate good shares "
        "(issue #6)."
    ),
    "gov.economic_assumptions.energy_prices.electricity_growth": (
        "One quarterly growth rate (energy_prices.obr.utilities) moves "
        "electricity and gas together (issue #2)."
    ),
    "gov.ofgem.standing_charge": (
        "No unit rate or standing charge parameters (issue #4)."
    ),
    "gov.ofgem.energy_price_cap": (
        "Values mix the 2023 and 2026 typical consumption bases across July "
        "2026, and epg_subsidy scales by their ratio (issue #3)."
    ),
    "cold_weather_payment": (
        "No Cold Weather Payment variable (policyengine-uk#435). Scotland "
        "pays the Winter Heating Payment instead, so coverage is not GB."
    ),
}

# The first policyengine-uk release on PyPI with each path in the form this
# dashboard reads it (path matrix on issue #1). The Warm Home Discount and
# the Great Britain electricity VAT rate exist from 2.165.1, but 2.165.1
# ends the zero VAT rate on 1 April 2027 (before the Budget); the
# Household Energy Payment, the energy price indices and the 1 July 2027
# end date arrive in 2.170.2. A Budget-era baseline needs 2.170.2 or later
# for every path (BUDGET_ERA_ENGINE).
MIN_ENGINE: dict[str, str] = {
    "gov.economic_assumptions.energy_prices.obr.utilities": "2.170.2",
    "gov.treasury.household_energy_payment.amount": "2.170.2",
    "gov.treasury.household_energy_payment.bands": "2.170.2",
    "gov.treasury.household_energy_payment.countries": "2.170.2",
    "gov.ofgem.warm_home_discount.amount": "2.165.1",
    "gov.ofgem.warm_home_discount.qualifying_benefits": "2.165.1",
    "gov.hmrc.vat.domestic_electricity_rate.great_britain": "2.165.1",
}

BUDGET_ERA_ENGINE = "2.170.2"


def model_limit_reason(path: str) -> str | None:
    for limited, reason in MODEL_LIMITS.items():
        if path == limited or path.startswith(limited + "."):
            return reason
    return None


def needs_newer_engine(path: str) -> str | None:
    """Minimum policyengine-uk version for a path, if it has one."""
    return MIN_ENGINE.get(path)


def warn_if_model_limited(path: str) -> None:
    reason = model_limit_reason(path)
    if reason:
        warnings.warn(f"{path}: {reason}", ModelLimitedWarning, stacklevel=3)
