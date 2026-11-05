"""Household calculator: example households, bills and support.

Runs locally with no model: bills come from Ofgem rates and kWh, support
from the rules below. On the day the same presets go to the model
(``policyengine_uk``) for net income, and the page checks that the two
agree on support amounts (tests/test_household.py).

Support rules (2026-27, current law):
- Household Energy Payment: £100, England, council tax bands A to D.
- Warm Home Discount: £150, England and Wales, a qualifying benefit
  (Pension Credit, Universal Credit, Housing Benefit, income-related ESA).
- Winter Fuel Payment: £200 per household with someone of State Pension
  age, £300 with someone aged 80 or over; recovered through income tax
  above £35,000 taxable income (not shown in this calculator).
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


PRESETS: tuple[Preset, ...] = (
    Preset("typical_dd", "Typical use, Direct Debit, dual fuel",
           2500, 9500, "direct_debit", "ENGLAND", "D", False, 45),
    Preset("low_use_prepay_flat", "Low use flat on prepayment",
           1800, 5000, "prepayment", "ENGLAND", "A", True, 32),
    Preset("high_use_family", "High-use family home",
           3600, 14000, "direct_debit", "ENGLAND", "E", False, 44),
    Preset("electric_only_e7", "Electric-only flat on Economy 7",
           3400, 0, "economy_7_direct_debit", "ENGLAND", "B", False, 58),
    Preset("pensioner_couple_band_b", "Pensioner couple on Pension Credit, band B",
           2700, 11000, "direct_debit", "ENGLAND", "B", True, 81),
    Preset("working_family_band_e", "Working family in band E",
           2900, 10500, "direct_debit", "ENGLAND", "E", False, 40),
    Preset("scotland_band_c", "Pensioner in Scotland, band C",
           2500, 9500, "direct_debit", "SCOTLAND", "C", True, 70),
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
        total = levels["economy_7_direct_debit"] * preset.electricity_kwh / multi
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
    whd = (
        o["whd_amount"]
        if preset.country in WHD_COUNTRIES and preset.qualifying_benefit
        else 0
    )
    if preset.oldest_age >= 80:
        wfp = o["wfp_higher"]
    elif preset.oldest_age >= 66:
        wfp = o["wfp_lower"]
    else:
        wfp = 0
    return {
        "household_energy_payment": float(hep),
        "warm_home_discount": float(whd),
        "winter_fuel_payment": float(wfp),
        "total": float(hep + whd + wfp),
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
                s: bill(preset, cap.price_factor(s))["total"] for s in scenarios
            },
        }
        rows.append(row)
    return rows
