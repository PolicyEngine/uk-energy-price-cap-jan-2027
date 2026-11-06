"""Household calculator: example households, bills and support.

Runs locally with no model: bills come from Ofgem rates and kWh, support
from the rules below. On the day the same presets go to the model
(``policyengine_uk``) for net income, and the page checks that the two
agree on support amounts (tests/test_household.py).

Support rules (2026-27, current law):
- Household Energy Payment: £100, England, council tax bands A to D.
- Warm Home Discount: £150. England and Wales: a qualifying benefit
  (Pension Credit, Universal Credit, Housing Benefit, income-related ESA).
  Scotland runs its own scheme: Core Group 1 (Pension Credit Guarantee
  Credit) is paid automatically; the Broader Group depends on the
  supplier and is not shown. policyengine-uk does not compute the Scottish
  scheme, so the model and this calculator differ there by design.
- Winter Fuel Payment (England and Wales): £200 per household with
  someone of State Pension age, £300 with someone aged 80 or over;
  recovered through income tax above £35,000 taxable income (not shown).
- Pension Age Winter Heating Payment (Scotland, in place of the Winter
  Fuel Payment): £211.15 under 80 and £316.70 at 80 or over in 2026-27
  (policyengine-uk 2.175.7 gov.social_security_scotland.pawhp, from the
  Scottish statutory instruments; check against mygov.scot before the
  day).
"""

from dataclasses import asdict, dataclass

from uk_energy_price_cap import cap

HEP_AMOUNT = 100
HEP_BANDS = ("A", "B", "C", "D")
HEP_COUNTRIES = ("ENGLAND",)
WHD_AMOUNT = 150
WHD_COUNTRIES = ("ENGLAND", "WALES")
WFP_LOWER = 200
WFP_HIGHER = 300
PAWHP_LOWER = 211.15
PAWHP_HIGHER = 316.70


@dataclass(frozen=True)
class Preset:
    id: str
    label: str
    electricity_kwh: float
    gas_kwh: float
    payment_method: str  # direct_debit, prepayment, economy_7_direct_debit
    country: str
    council_tax_band: str
    qualifying_benefit: bool
    oldest_age: int
    pension_credit: bool = False


PRESETS: tuple[Preset, ...] = (
    Preset(
        "typical_dd",
        "Typical use, Direct Debit, dual fuel",
        2500,
        9500,
        "direct_debit",
        "ENGLAND",
        "D",
        False,
        45,
    ),
    Preset(
        "low_use_prepay_flat",
        "Low use flat on prepayment",
        1800,
        5000,
        "prepayment",
        "ENGLAND",
        "A",
        True,
        32,
    ),
    Preset(
        "high_use_family",
        "High-use family home",
        3600,
        14000,
        "direct_debit",
        "ENGLAND",
        "E",
        False,
        44,
    ),
    Preset(
        "electric_only_e7",
        "Electric-only flat on Economy 7",
        3400,
        0,
        "economy_7_direct_debit",
        "ENGLAND",
        "B",
        False,
        58,
    ),
    Preset(
        "pensioner_couple_band_b",
        "Pensioner couple on Pension Credit, band B",
        2700,
        11000,
        "direct_debit",
        "ENGLAND",
        "B",
        True,
        81,
        pension_credit=True,
    ),
    Preset(
        "working_family_band_e",
        "Working family in band E",
        2900,
        10500,
        "direct_debit",
        "ENGLAND",
        "E",
        False,
        40,
    ),
    Preset(
        "scotland_band_c",
        "Pensioner on Pension Credit in Scotland, band C",
        2500,
        9500,
        "direct_debit",
        "SCOTLAND",
        "C",
        True,
        70,
        pension_credit=True,
    ),
)

BY_ID = {p.id: p for p in PRESETS}


def _method_factor(method: str) -> float:
    """Payment method relative to Direct Debit, from the current cap levels.

    Placeholder: one ratio on the whole bill. On the day, Annex 9 rates by
    payment method replace it.
    """
    levels = cap.CAP["payment_methods"][cap.CURRENT_PERIOD]
    if method == "economy_7_direct_debit":
        return 1.0  # priced from the Economy 7 level below
    return levels[method] / levels["direct_debit"]


def bill(preset: Preset, factor: float = 1.0) -> dict[str, float]:
    """Annual bill at current rates scaled by ``factor``."""
    if preset.payment_method == "economy_7_direct_debit":
        levels = cap.CAP["payment_methods"][cap.CURRENT_PERIOD]
        multi = cap.CAP["tdcv_bases"][cap.CURRENT_BASIS]["multi_register_kwh"]
        total = (
            levels["economy_7_direct_debit"] * preset.electricity_kwh / multi
        )
        total = cap.pence_to_pounds(total * factor)
        return {"electricity": total, "gas": 0.0, "total": total}
    rates = cap.scaled_rates(factor * _method_factor(preset.payment_method))
    return cap.annual_bill(preset.electricity_kwh, preset.gas_kwh, rates)


def support(preset: Preset, overrides: dict | None = None) -> dict[str, float]:
    """Current-law support for a preset; ``overrides`` changes amounts or rules."""
    o = {
        "hep_amount": HEP_AMOUNT,
        "hep_bands": HEP_BANDS,
        "hep_countries": HEP_COUNTRIES,
        "whd_amount": WHD_AMOUNT,
        "wfp_lower": WFP_LOWER,
        "wfp_higher": WFP_HIGHER,
        **(overrides or {}),
    }
    hep = (
        o["hep_amount"]
        if preset.country in o["hep_countries"]
        and preset.council_tax_band in o["hep_bands"]
        else 0
    )
    if preset.country in WHD_COUNTRIES:
        gets_whd = preset.qualifying_benefit
    elif preset.country == "SCOTLAND":
        gets_whd = preset.pension_credit  # Core Group 1 only
    else:
        gets_whd = False
    whd = o["whd_amount"] if gets_whd else 0
    scotland = preset.country == "SCOTLAND"
    if preset.oldest_age >= 80:
        winter = PAWHP_HIGHER if scotland else o["wfp_higher"]
    elif preset.oldest_age >= 66:
        winter = PAWHP_LOWER if scotland else o["wfp_lower"]
    else:
        winter = 0
    wfp = 0 if scotland else winter
    pawhp = winter if scotland else 0
    return {
        "household_energy_payment": float(hep),
        "warm_home_discount": float(whd),
        "winter_fuel_payment": float(wfp),
        "pension_age_winter_heating_payment": float(pawhp),
        "total": round(float(hep + whd + wfp + pawhp), 2),
    }


def calculate(preset_id: str, scenario_id: str = "central") -> dict:
    """Bills now and under a scenario, the change, and support."""
    preset = BY_ID[preset_id]
    now = bill(preset)
    then = bill(preset, cap.price_factor(scenario_id))
    sup = support(preset)
    change = cap.pence_to_pounds(then["total"] - now["total"])
    return {
        "preset": asdict(preset),
        "scenario_id": scenario_id,
        "bill_oct_dec_2026": now,
        "bill_jan_mar_2027": then,
        "annual_change": change,
        "support": sup,
        "change_after_support": cap.pence_to_pounds(change - sup["total"]),
    }


def all_presets(scenarios: list[str] | None = None) -> list[dict]:
    scenarios = scenarios or cap.scenario_ids()
    rows = []
    for preset in PRESETS:
        row = {
            "id": preset.id,
            "label": preset.label,
            "inputs": asdict(preset),
            "bill_oct_dec_2026": bill(preset)["total"],
            "support": support(preset),
            "bill_jan_mar_2027": {
                s: bill(preset, cap.price_factor(s))["total"]
                for s in scenarios
            },
        }
        rows.append(row)
    return rows
