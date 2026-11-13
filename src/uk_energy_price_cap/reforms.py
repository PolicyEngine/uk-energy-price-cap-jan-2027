"""Measure registry: every candidate lever for the January 2027 cap.

PLACEHOLDERS. Every entry below has status ``placeholder``: its values are
illustrative settings taken from the planning range in
docs/candidate-reforms.md, not announced policy. The publication gate
(``publication.validate``) holds every placeholder back from a public
results file. On the day the integrator replaces each value with the
announced one, sets ``status`` to ``announced`` and records the source in
docs/candidate-reforms.md, in waves: parameters, then modifiers, then new
variables (docs/RUNBOOK.md).

Charts, the household calculator and the ledger read the measure list from
here. No component keeps a list of its own.
"""

from uk_energy_price_cap import cap
from uk_energy_price_cap.measure_templates import (
    amount_change,
    cap_shock,
    list_change,
    quarterly_growth_change,
    rate_change,
)
from uk_energy_price_cap.models import Reform, Route, Status

# Placeholder cap level for January to March 2027 (central of the
# planning range, docs/candidate-reforms.md). Replace with Ofgem's figure.
PLACEHOLDER_Q1_CAP = 2013  # drill 7 MOCK release, corrected 11:15, Direct Debit, 2026 basis
OCT_DEC_2026_CAP = 1723  # Ofgem, 2026 typical consumption basis
# The typical bill the OBR's path implies for January to March 2027 (EFO
# October 2026, para 2.22), on the 2026 basis: the baseline the lever moves.
OBR_Q1_2027_CAP = cap.scenario("obr_path")["direct_debit"]
# The OBR's year-on-year CPI utilities rates the lever replaces, as in
# policyengine-uk 2.177.7 energy_prices/obr.yaml (tests/engine checks them
# against the installed engine).
OBR_UTILITIES = {"2027Q1": 0.113241, "2028Q1": -0.105705}


def cap_q1_2027_changes(q1_cap: float = PLACEHOLDER_Q1_CAP) -> dict:
    """The cap lever for a January to March 2027 level (2026 basis).

    Raises the 2027Q1 index level by ``q1_cap / OBR_Q1_2027_CAP`` against
    the baseline and offsets 2028Q1, so prices return to the OBR path from
    April 2027 and fiscal 2027-28 is unchanged (docs/METHOD.md; the choice
    is open on the readiness issue).
    """
    g, g_next = cap_shock(
        q1_cap,
        OBR_Q1_2027_CAP,
        OBR_UTILITIES["2027Q1"],
        OBR_UTILITIES["2028Q1"],
    )
    return quarterly_growth_change(
        ENERGY_PRICE_PATH, {"2027Q1": g, "2028Q1": g_next}
    )


ENERGY_PRICE_PATH = "gov.economic_assumptions.energy_prices.obr.utilities"
HEP = "gov.treasury.household_energy_payment"
WHD = "gov.ofgem.warm_home_discount"
ELEC_VAT_GB = "gov.hmrc.vat.domestic_electricity_rate.great_britain"
BILL_CREDIT = "gov.treasury.energy_bills_rebate.energy_bills_credit"
WFP = "gov.dwp.winter_fuel_payment.amount"

PH = Status.PLACEHOLDER

REFORMS: list[Reform] = [
    Reform(
        id="cap_q1_2027",
        name="Energy price cap, January to March 2027",
        description=(
            "Placeholder. Moves household electricity and gas prices for "
            "January to March 2027 from the forecast path in the model to "
            "the announced cap, as one percentage change on both fuels. "
            "Prices return to the forecast path from April 2027."
        ),
        parameter_changes=cap_q1_2027_changes(),
        route=Route.DASHBOARD_PARAM,
        status=PH,
        lever="bills",
        likelihood="certain",
    ),
    Reform(
        id="hep_top_up",
        name="Larger Household Energy Payment",
        description=(
            "Placeholder. Raises the Household Energy Payment for "
            "households in council tax bands A to D in England from £100 "
            "to £200 in 2026-27."
        ),
        parameter_changes=amount_change(f"{HEP}.amount", {"2026": 200}),
        route=Route.DASHBOARD_PARAM,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="medium",
    ),
    Reform(
        id="hep_second_apr_2027",
        name="Second Household Energy Payment, April 2027",
        description=(
            "Placeholder. A second £100 Household Energy Payment for "
            "households in council tax bands A to D in England, paid in "
            "April 2027 (fiscal 2027-28)."
        ),
        parameter_changes=amount_change(f"{HEP}.amount", {"2027": 100}),
        route=Route.DASHBOARD_PARAM,
        status=PH,
        lever="support",
        likelihood="announced",
    ),
    Reform(
        id="hep_band_e",
        name="Household Energy Payment extended to band E",
        description=(
            "Placeholder. Pays the £100 Household Energy Payment to "
            "households in council tax bands A to E in England."
        ),
        parameter_changes=list_change(
            f"{HEP}.bands", {"2026": ["A", "B", "C", "D", "E"]}
        ),
        route=Route.DASHBOARD_PARAM,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="low",
    ),
    Reform(
        id="hep_great_britain",
        name="Household Energy Payment in Scotland and Wales",
        description=(
            "Placeholder. Pays the £100 to households in bands A to D in "
            "Scotland and Wales as well as England. Both devolved "
            "governments have been reported as planning this; neither "
            "official source is confirmed yet. Band valuations differ by "
            "nation."
        ),
        parameter_changes=list_change(
            f"{HEP}.countries",
            {"2026": ["ENGLAND", "SCOTLAND", "WALES"]},
        ),
        route=Route.DASHBOARD_PARAM,
        status=PH,
        lever="support",
        likelihood="medium",
    ),
    Reform(
        id="whd_uplift",
        name="Larger Warm Home Discount",
        description=(
            "Placeholder. Raises the Warm Home Discount from £150 to £250 "
            "for the 2026-27 scheme year (England and Wales)."
        ),
        parameter_changes=amount_change(f"{WHD}.amount", {"2026": 250}),
        route=Route.DASHBOARD_PARAM,
        status=PH,
        lever="support",
        likelihood="medium",
    ),
    Reform(
        id="whd_disability_benefits",
        name="Warm Home Discount for disability benefit recipients",
        description=(
            "Placeholder. Adds Personal Independence Payment and "
            "Attendance Allowance to the benefits that qualify for the Warm "
            "Home Discount."
        ),
        parameter_changes=list_change(
            f"{WHD}.qualifying_benefits",
            {
                "2026": [
                    "pension_credit",
                    "universal_credit",
                    "housing_benefit",
                    "esa_income",
                    "pip",
                    "attendance_allowance",
                ]
            },
        ),
        route=Route.DASHBOARD_PARAM,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="low",
    ),
    Reform(
        id="electricity_vat_to_march_2028",
        name="0% VAT on domestic electricity to March 2028",
        description=(
            "Placeholder. Keeps the 0% VAT rate on domestic electricity in "
            "Great Britain from 1 July 2027, when it is due to return to "
            "5%, to 31 March 2028."
        ),
        parameter_changes=rate_change(
            ELEC_VAT_GB, {"2027-07-01.2028-03-31": 0.0}
        ),
        route=Route.DASHBOARD_PARAM,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="medium",
    ),
    Reform(
        id="gas_vat_zero",
        name="0% VAT on domestic gas",
        description="Placeholder. Cuts VAT on domestic gas from 5% to 0%.",
        route=Route.NEEDS_PE_UK_FIRST,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="low",
        limit_reason=(
            "The model has no VAT rate for gas alone: gas shares the "
            "reduced rate with other goods, so cutting it would cut theirs "
            "too (issue #6)."
        ),
    ),
    Reform(
        id="universal_bill_credit",
        name="Credit on every household energy bill",
        description=(
            "Placeholder. A £150 credit to every household with an "
            "electricity account in 2026-27."
        ),
        parameter_changes=amount_change(BILL_CREDIT, {"2026": 150}),
        route=Route.DASHBOARD_PARAM,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="low",
    ),
    Reform(
        id="wfp_top_up",
        name="Larger Winter Fuel Payment",
        description=(
            "Placeholder. Adds £100 a household to the Winter Fuel Payment "
            "for 2026-27: £300 to £400 for the higher rate and £200 to £300 "
            "for the lower, with each shared rate (two eligible people in "
            "one household) raised by £50. Scotland pays its own Pension "
            "Age Winter Heating Payment instead, which this lever does not "
            "change."
        ),
        parameter_changes={
            **amount_change(f"{WFP}.higher", {"2026": 400}),
            **amount_change(f"{WFP}.lower", {"2026": 300}),
            **amount_change(
                f"{WFP}.higher_shared_with_80_or_over", {"2026": 200}
            ),
            **amount_change(
                f"{WFP}.higher_shared_with_under_80", {"2026": 250}
            ),
            **amount_change(f"{WFP}.lower_shared", {"2026": 150}),
        },
        route=Route.DASHBOARD_PARAM,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="low",
    ),
    Reform(
        id="targeted_energy_discount",
        name="Targeted energy discount",
        description=(
            "Placeholder. A discount of £175 a year for households whose "
            "highest individual income is below £24,000 or who receive a "
            "means-tested benefit."
        ),
        route=Route.NEEDS_PE_UK_FIRST,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="medium",
        limit_reason=(
            "The model has no rule for this discount yet: it exists in an "
            "earlier PolicyEngine analysis and must be added and checked "
            "before it can be estimated."
        ),
    ),
    Reform(
        id="gas_standing_charge_removal",
        name="Gas standing charge moved into the unit rate",
        description=(
            "Placeholder. Removes the gas standing charge and recovers the "
            "cost through a higher unit rate, so that bills raise the same "
            "total."
        ),
        route=Route.NOT_COMPUTABLE,
        status=PH,
        lever="bills",
        likelihood="announced",
        limit_reason=(
            "The data hold gas spending in pounds, not kWh, and do not say "
            "which homes are on mains gas, so moving the standing charge "
            "into the unit rate cannot be estimated (issue #4)."
        ),
    ),
    Reform(
        id="electricity_standing_charge_shift",
        name="Part of the electricity standing charge moved into the unit rate",
        description=(
            "Placeholder. Moves half of the electricity standing charge "
            "into the unit rate."
        ),
        route=Route.NOT_COMPUTABLE,
        status=Status.WITHDRAWN,
        lever="bills",
        likelihood="low",
        limit_reason=(
            "The data hold electricity spending in pounds, not kWh or "
            "tariff type, so a change to the standing charge cannot be "
            "estimated (issue #4)."
        ),
    ),
    Reform(
        id="price_guarantee",
        name="Bills held at a set typical level",
        description=(
            "Placeholder. A subsidy per unit that holds the typical Direct "
            "Debit bill at £1,723 for January to March 2027."
        ),
        route=Route.NEEDS_PE_UK_FIRST,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="low",
        limit_reason=(
            "The model's record of past cap levels changes how it measures "
            "typical use in July 2026, so a subsidy based on it would be "
            "about 11% out (issue #3)."
        ),
    ),
    Reform(
        id="levies_off_electricity",
        name="Remaining policy costs moved off electricity bills",
        description=(
            "Placeholder. Moves the remaining Renewables Obligation and "
            "Feed-in Tariff costs from electricity bills into taxation."
        ),
        route=Route.NEEDS_PE_UK_FIRST,
        status=Status.WITHDRAWN,
        lever="bills",
        likelihood="low",
        limit_reason=(
            "The model moves electricity and gas prices together, so a "
            "change to electricity bills alone cannot be estimated "
            "(issue #2)."
        ),
    ),
    Reform(
        id="cold_weather_payment",
        name="Larger Cold Weather Payment",
        description="Placeholder. Raises the payment from £25 to £50 for each 7-day cold spell in winter 2026-27.",
        route=Route.NEEDS_PE_UK_FIRST,
        status=PH,
        lever="support",
        likelihood="low",
        limit_reason=(
            "The model does not include the Cold Weather Payment (issue #8)."
        ),
    ),
    Reform(
        id="energy_debt_relief",
        name="Energy debt relief",
        description=(
            "Placeholder. One-off relief for households with energy debt "
            "on means-tested or disability benefits."
        ),
        route=Route.LEDGER,
        status=Status.WITHDRAWN,
        lever="support",
        likelihood="announced",
        limit_reason=(
            "The data do not record energy debt, so the official figure is "
            "recorded, not estimated."
        ),
    ),
    Reform(
        id="prepayment_levelisation",
        name="Prepayment levelisation",
        description=(
            "Placeholder. Changes to how prepayment and Direct Debit costs "
            "are levelled."
        ),
        route=Route.NOT_COMPUTABLE,
        status=PH,
        lever="bills",
        likelihood="low",
        limit_reason=(
            "The data show which homes use prepayment meters, but the model "
            "has no prices by payment method (issue #4)."
        ),
    ),
]

BY_ID: dict[str, Reform] = {r.id: r for r in REFORMS}


def get(reform_id: str) -> Reform:
    return BY_ID[reform_id]


def computable() -> list[Reform]:
    return [r for r in REFORMS if r.is_computable]


def ledger_rows() -> list[dict[str, str]]:
    """One coverage-ledger line per measure (docs/RUNBOOK.md, G1)."""
    return [
        {
            "id": r.id,
            "name": r.name,
            "route": r.route.value,
            "status": r.status.value,
            "lever": r.lever,
            "likelihood": r.likelihood,
            "reason": r.limit_reason or "",
        }
        for r in REFORMS
    ]
