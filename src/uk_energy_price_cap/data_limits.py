"""Inputs the data do not hold (pruned from the Autumn Budget 2026 module).

A measure that acts only through one of these inputs is published as not
computable, with the reason, and never as £0. Microcosm holds household
energy spend in pounds (``electricity_consumption``, ``gas_consumption``),
a prepayment flag (``uses_energy_prepayment_meter``, 12.6% of households
on build 6f918b81) and council tax band. It also exports household
``gas_kwh`` and ``electricity_kwh`` (calendar 2024), which policyengine-uk
does not expose: ``household_kwh.py`` reads them from the file with h5py
and joins on ``household_id``. ``gas_kwh > 0`` identifies gas households.
It holds no tariff or payment method other than prepayment, heating fuel
or energy debt (audit of build a6299504, 5 November 2026, issue #4;
kWh columns per María Juaristi, 13 November 2026).
"""

import warnings


class DataLimitedWarning(UserWarning):
    """A reform touches an input the data do not hold."""


# Variable -> why changing it, or a rule keyed on it, moves no one.
DATA_LIMITS: dict[str, str] = {
    "electricity_consumption_kwh": (
        "The engine's monthly kWh input defaults to -1 and stays unfilled "
        "until policyengine-uk#2890 item 1; the file's electricity_kwh "
        "column is read directly instead (household_kwh.py)."
    ),
    "gas_consumption_kwh": (
        "The engine's monthly kWh input defaults to -1 and stays unfilled "
        "until policyengine-uk#2890 item 1; the file's gas_kwh column is "
        "read directly instead (household_kwh.py)."
    ),
    "energy_payment_method": (
        "Only a prepayment flag is held; Direct Debit, Standard Credit and "
        "Economy 7 are not distinguished (issue #4)."
    ),
    "has_mains_gas": (
        "No mains gas variable in the engine; gas_kwh > 0 in the file "
        "identifies gas households (matches gas_consumption > 0 on every "
        "row, 24.3m households on build 6f918b81)."
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
