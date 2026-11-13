"""Every registered lever moves what it should in policyengine-uk.

Skipped unless the model extra is installed (``uv sync --extra model``):
CI runs the core package only. Single-household situations, no microdata,
so these are light and need no lock.

Levers go to the engine as a reform dict (``Simulation(reform=...)``), as
pipeline.build_model passes them: ``Scenario(parameter_changes=...)``
refuses list values such as council tax bands or qualifying benefits.

A lever that changes nothing is the failure this guards against: a lone
date key changes one day of a parameter (measure_templates._period), and a
year-on-year rate keyed by calendar year moves every quarter of it.
"""

import warnings

import pytest

pytest.importorskip("policyengine_uk")

from policyengine_uk import Simulation  # noqa: E402

from uk_energy_price_cap import reforms  # noqa: E402

P = "gov.economic_assumptions.energy_prices"


def _situation(
    country_region="NORTH_EAST",
    band="B",
    ages=(72,),
    person=None,
    household=None,
):
    years = (2026, 2027)
    people = {}
    for i, age in enumerate(ages):
        people[f"p{i}"] = {"age": {y: age + (y - 2026) for y in years}}
        people[f"p{i}"].update(person or {})
    return {
        "people": people,
        "benunits": {"b": {"members": list(people)}},
        "households": {
            "h": {
                "members": list(people),
                "region": {y: country_region for y in years},
                "council_tax_band": {y: band for y in years},
                "electricity_consumption": {2024: 1000},
                "gas_consumption": {2024: 700},
                "would_receive_warm_home_discount": {y: True for y in years},
                **(household or {}),
            }
        },
    }


PENSION_CREDIT = {"pension_credit_reported": {2026: 3000, 2027: 3000}}
# Earnings keep the household off Universal Credit, so only PIP qualifies.
PIP = {
    "pip": {2026: 5000, 2027: 5000},
    "employment_income": {2026: 30000, 2027: 30000},
}

# measure id -> (situation, variable, year)
CASES = {
    "hep_top_up": (_situation(), "household_energy_payment", 2026),
    "hep_second_apr_2027": (_situation(), "household_energy_payment", 2027),
    "hep_band_e": (_situation(band="E"), "household_energy_payment", 2026),
    "hep_great_britain": (
        _situation("SCOTLAND"),
        "household_energy_payment",
        2026,
    ),
    "whd_uplift": (
        _situation(person=PENSION_CREDIT),
        "warm_home_discount",
        2026,
    ),
    "whd_disability_benefits": (
        _situation(ages=(45,), person=PIP),
        "warm_home_discount",
        2026,
    ),
    "electricity_vat_to_march_2028": (
        _situation(),
        "domestic_energy_vat",
        2027,
    ),
    "universal_bill_credit": (_situation(), "ebr_energy_bills_credit", 2026),
    "wfp_top_up": (_situation(), "winter_fuel_allowance", 2026),
}


def _run(changes, situation, variable, year):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sim = Simulation(situation=situation, reform=changes)
        value = float(sim.calculate(variable, year).sum())
    period_warnings = [
        str(w.message) for w in caught if "Period" in type(w.message).__name__
    ]
    return value, period_warnings


def test_every_support_lever_has_a_case():
    support = {r.id for r in reforms.computable() if r.lever == "support"}
    assert support == set(CASES)


@pytest.mark.parametrize("measure_id", sorted(CASES))
def test_lever_changes_its_variable_without_a_period_warning(measure_id):
    situation, variable, year = CASES[measure_id]
    changes = reforms.get(measure_id).parameter_changes
    base, _ = _run(None, situation, variable, year)
    reformed, period_warnings = _run(changes, situation, variable, year)
    assert period_warnings == []
    assert reformed != pytest.approx(base), (measure_id, base, reformed)


def test_shared_winter_fuel_rates_are_topped_up():
    # Two people over State Pension age, one 80 or over: shared rates.
    situation = _situation(ages=(82, 75))
    changes = reforms.get("wfp_top_up").parameter_changes
    base, _ = _run(None, situation, "winter_fuel_allowance", 2026)
    reformed, _ = _run(changes, situation, "winter_fuel_allowance", 2026)
    assert reformed - base == pytest.approx(100)


def test_vat_extension_ends_in_march_2028():
    changes = reforms.get("electricity_vat_to_march_2028").parameter_changes
    sim = Simulation(situation=_situation(), reform=changes)
    rate = sim.tax_benefit_system.parameters(
        "2028-04-01"
    ).gov.hmrc.vat.domestic_electricity_rate.great_britain
    assert rate == pytest.approx(0.05)


def _levels(changes):
    sim = Simulation(situation=_situation(), reform=changes)
    p = sim.tax_benefit_system.parameters.gov.economic_assumptions
    q = p.energy_prices.quarterly
    obr = p.energy_prices.obr.utilities
    out = {}
    for year in (2026, 2027, 2028):
        for n, month in ((1, "01"), (2, "04"), (3, "07"), (4, "10")):
            day = f"{year}-{month}-01"
            out[(year, n)] = (q.electricity(day), q.gas(day))
    fiscal = {
        y: (
            p.energy_prices.fiscal_year.electricity(f"{y}-01-01"),
            p.energy_prices.fiscal_year.gas(f"{y}-01-01"),
        )
        for y in (2026, 2027)
    }
    return out, fiscal, obr


def test_obr_rates_in_the_registry_match_the_engine():
    _, _, obr = _levels(None)
    assert obr("2027-01-01") == pytest.approx(reforms.OBR_UTILITIES["2027Q1"])
    assert obr("2028-01-01") == pytest.approx(reforms.OBR_UTILITIES["2028Q1"])


def test_cap_lever_moves_only_january_to_march_2027():
    base, base_fy, _ = _levels(None)
    reform, reform_fy, _ = _levels(
        reforms.get("cap_q1_2027").parameter_changes
    )
    target = reforms.PLACEHOLDER_Q1_CAP / reforms.OBR_Q1_2027_CAP
    for quarter in base:
        expected = target if quarter == (2027, 1) else 1.0
        for fuel in (0, 1):
            ratio = reform[quarter][fuel] / base[quarter][fuel]
            assert ratio == pytest.approx(expected, abs=1e-5), quarter
    # Fiscal 2027-28 is unchanged: the gap lasts one quarter.
    assert reform_fy[2027] == pytest.approx(base_fy[2027])
    assert reform_fy[2026][0] > base_fy[2026][0]


def test_second_hep_pays_exactly_100_in_2027_28():
    situation, variable, year = CASES["hep_second_apr_2027"]
    changes = reforms.get("hep_second_apr_2027").parameter_changes
    base, _ = _run(None, situation, variable, year)
    reformed, _ = _run(changes, situation, variable, year)
    assert (base, reformed) == (0, 100)
