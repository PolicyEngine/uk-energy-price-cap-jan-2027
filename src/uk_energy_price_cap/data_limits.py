"""Inputs the data do not hold (pruned from the Autumn Budget 2026 module).

A measure that acts only through one of these inputs is published as not
computable, with the reason, and never as £0. Microcosm holds household
energy spend in pounds (``electricity_consumption``, ``gas_consumption``),
a prepayment flag and council tax band. It holds no kilowatt-hours, tariff
or payment method other than prepayment, heating fuel, mains gas flag or
energy debt (audit of build a6299504, 5 November 2026; issue #4).
"""

import warnings


class DataLimitedWarning(UserWarning):
    """A reform touches an input the data do not hold."""


# Variable -> why changing it, or a rule keyed on it, moves no one.
DATA_LIMITS: dict[str, str] = {
    "electricity_consumption_kwh": (
        "Microcosm holds electricity spend in pounds only; the kWh input "
        "defaults to -1 and is not filled (issue #4)."
    ),
    "gas_consumption_kwh": (
        "Microcosm holds gas spend in pounds only; the kWh input defaults "
        "to -1 and is not filled (issue #4)."
    ),
    "energy_payment_method": (
        "Only a prepayment flag is held; Direct Debit, Standard Credit and "
        "Economy 7 are not distinguished (issue #4)."
    ),
    "has_mains_gas": (
        "No mains gas flag; gas spend above zero is the only proxy "
        "(issue #4)."
    ),
    "main_heating_fuel": "No heating fuel variable (issue #4).",
    "energy_debt": "No energy arrears in the survey data.",
}

# Parameters whose effect runs only through a data-limited input.
DATA_LIMITED_PARAMETERS: dict[str, str] = {}


def data_limit_reason(name: str) -> str | None:
    """The reason a variable or parameter is data-limited, or None."""
    return DATA_LIMITS.get(name) or DATA_LIMITED_PARAMETERS.get(name)


def warn_if_data_limited(name: str) -> None:
    reason = data_limit_reason(name)
    if reason:
        warnings.warn(f"{name}: {reason}", DataLimitedWarning, stacklevel=3)
