"""Generate ``dashboard/public/data/results.json``.

Two sources, one output schema (docs/RESULTS_SCHEMA.md):

- ``placeholder`` (default, what CI runs): synthetic households built here
  from a fixed seed. No microdata, no model. Every figure is a placeholder
  and the file says so in ``meta``.
- ``model`` (the day): Microcosm through policyengine-uk. Not wired until
  the engine and data pair is certified (issue #1); it refuses to run
  while ``sign_off.REQUIRED`` is on and no freeze record exists.

Each household's bill change is its electricity and gas spend times the
change in prices, at the January to March 2027 rates for a full year
(annualised). Northern Ireland is outside the Ofgem cap and is excluded
from the cap shock; it is shown as its own row.
"""

import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from uk_energy_price_cap import cap, household, publication, reforms, years

HOUSEHOLDS_UK = 28_900_000
# Fixed so the committed placeholder file is reproducible byte for byte.
TEMPLATE_DATE = "2026-11-05"
REGIONS = [
    ("NORTH_EAST", "ENGLAND", 0.042), ("NORTH_WEST", "ENGLAND", 0.112),
    ("YORKSHIRE", "ENGLAND", 0.083), ("EAST_MIDLANDS", "ENGLAND", 0.072),
    ("WEST_MIDLANDS", "ENGLAND", 0.086), ("EAST_OF_ENGLAND", "ENGLAND", 0.094),
    ("LONDON", "ENGLAND", 0.124), ("SOUTH_EAST", "ENGLAND", 0.138),
    ("SOUTH_WEST", "ENGLAND", 0.088), ("WALES", "WALES", 0.049),
    ("SCOTLAND", "SCOTLAND", 0.084), ("NORTHERN_IRELAND", "NORTHERN_IRELAND", 0.028),
]
TENURES = [
    ("OWNED_OUTRIGHT", 0.37), ("OWNED_WITH_MORTGAGE", 0.26),
    ("RENT_FROM_COUNCIL", 0.09), ("RENT_FROM_HA", 0.09),
    ("RENT_PRIVATELY", 0.19),
]
BANDS = [("A", 0.22), ("B", 0.19), ("C", 0.21), ("D", 0.16), ("E", 0.10),
         ("F", 0.06), ("G", 0.05), ("H", 0.01), ("I", 0.002)]
DIMENSIONS = ("region", "tenure", "council_tax_band", "fuel", "payment")


@dataclass
class SyntheticHousehold:
    decile: int
    region: str
    country: str
    tenure: str
    council_tax_band: str
    net_income: float
    electricity: float
    gas: float
    prepayment: bool
    qualifying_benefit: bool
    disability_benefit: bool
    oldest_age: int
    weight: float

    @property
    def fuel(self) -> str:
        return "dual_fuel" if self.gas > 0 else "electric_only"

    @property
    def payment(self) -> str:
        return "prepayment" if self.prepayment else "other"


def _pick(rng: random.Random, options):
    labels = [o[0] for o in options]
    shares = [o[-1] for o in options]
    return rng.choices(range(len(options)), weights=shares)[0], labels


def synthetic_households(n: int = 3000, seed: int = 20270101):
    """Synthetic households with plausible shapes. Not survey data."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        decile = i % 10 + 1
        r, _ = _pick(rng, REGIONS)
        region, country, _share = REGIONS[r]
        t, tenures = _pick(rng, TENURES)
        b, bands = _pick(rng, BANDS)
        income = 9_000 * decile ** 1.15 * rng.uniform(0.85, 1.15)
        electric_only = rng.random() < 0.16
        electricity = rng.uniform(650, 1_250) * (1.6 if electric_only else 1)
        electricity *= 0.9 + 0.02 * decile
        gas = 0.0 if electric_only else rng.uniform(450, 1_150)
        out.append(
            SyntheticHousehold(
                decile=decile,
                region=region,
                country=country,
                tenure=tenures[t],
                council_tax_band=bands[b],
                net_income=round(income, 2),
                electricity=round(electricity, 2),
                gas=round(gas, 2),
                prepayment=rng.random() < (0.25 if decile <= 3 else 0.08),
                qualifying_benefit=rng.random() < max(0.05, 0.6 - 0.07 * decile),
                disability_benefit=rng.random() < 0.12,
                oldest_age=rng.choice([30, 40, 50, 60, 68, 75, 82]),
                weight=HOUSEHOLDS_UK / n,
            )
        )
    return out


def _bill_change(h: SyntheticHousehold, factor: float) -> float:
    if h.country == "NORTHERN_IRELAND":
        return 0.0
    return (h.electricity + h.gas) * (factor - 1)


def _current_support(h: SyntheticHousehold) -> float:
    preset = household.Preset(
        "x", "x", 0, 0, "direct_debit", h.country, h.council_tax_band,
        h.qualifying_benefit, h.oldest_age,
    )
    return household.support(preset)["total"]


def _measure_gain(measure_id: str, h: SyntheticHousehold) -> tuple[int, float]:
    """(policy year, annual gain in £) for a computable support measure."""
    england_ad = h.country == "ENGLAND" and h.council_tax_band in "ABCD"
    ew = h.country in ("ENGLAND", "WALES")
    if measure_id == "hep_top_up":
        return 2026, 100.0 if england_ad else 0.0
    if measure_id == "hep_band_e":
        return 2026, 100.0 if (
            h.country == "ENGLAND" and h.council_tax_band == "E"
        ) else 0.0
    if measure_id == "hep_great_britain":
        return 2026, 100.0 if (
            h.country in ("SCOTLAND", "WALES") and h.council_tax_band in "ABCD"
        ) else 0.0
    if measure_id == "whd_uplift":
        return 2026, 150.0 if (ew and h.qualifying_benefit) else 0.0
    if measure_id == "whd_disability_benefits":
        return 2026, 150.0 if (
            ew and h.disability_benefit and not h.qualifying_benefit
        ) else 0.0
    if measure_id == "electricity_vat_to_march_2028":
        months = 9 / 12  # July 2027 to March 2028
        return 2027, h.electricity * 0.05 * months if h.country != "NORTHERN_IRELAND" else 0.0
    if measure_id == "universal_bill_credit":
        return 2026, 150.0 if h.country != "NORTHERN_IRELAND" else 0.0
    if measure_id == "wfp_top_up":
        return 2026, 100.0 if h.oldest_age >= 66 else 0.0
    raise KeyError(measure_id)


def _mean_cell(rows, value, floor=publication.DISCLOSURE_FLOOR):
    records = len(rows)
    weight = sum(h.weight for h in rows)
    if records < floor or weight == 0:
        return None
    return round(sum(value(h) * h.weight for h in rows) / weight, 2)


def _cell(value):
    return {"value": value} if value is not None else {"withheld": True}


def build_placeholder(n: int = 3000, seed: int = 20270101) -> dict:
    hh = synthetic_households(n, seed)
    by_decile = defaultdict(list)
    for h in hh:
        by_decile[h.decile].append(h)

    bills_by_decile = []
    bills_by_group = []
    for s in cap.scenario_ids():
        factor = cap.price_factor(s)
        for d in range(1, 11):
            rows = by_decile[d]
            gross = _mean_cell(rows, lambda h: _bill_change(h, factor))
            share = _mean_cell(
                rows, lambda h: 100 * _bill_change(h, factor) / h.net_income
            )
            net = _mean_cell(
                rows, lambda h: _bill_change(h, factor) - _current_support(h)
            )
            bills_by_decile.append({
                "scenario_id": s, "decile": d,
                "gross_change_gbp": _cell(gross),
                "share_of_net_income_pct": _cell(share),
                "change_after_support_gbp": _cell(net),
            })
        for dim in DIMENSIONS:
            groups = defaultdict(list)
            for h in hh:
                groups[getattr(h, dim)].append(h)
            for group in sorted(groups):
                bills_by_group.append({
                    "scenario_id": s, "dimension": dim, "group": group,
                    "outside_cap": group == "NORTHERN_IRELAND",
                    "gross_change_gbp": _cell(_mean_cell(
                        groups[group], lambda h: _bill_change(h, factor))),
                })

    measures = []
    decile_impact = []
    for r in reforms.REFORMS:
        entry = {
            "id": r.id, "name": r.name, "description": r.description,
            "route": r.route.value, "status": r.status.value,
            "lever": r.lever, "likelihood": r.likelihood,
            "computable": r.is_computable, "reason": r.limit_reason,
            "calculator_only": r.calculator_only,
            "year": None, "cost_gbp_m": None, "households_reached_m": None,
        }
        if r.is_computable and r.lever == "support":
            year = None
            total = 0.0
            reached = 0.0
            for h in hh:
                year, gain = _measure_gain(r.id, h)
                total += gain * h.weight
                reached += h.weight if gain > 0 else 0
            entry.update(
                year=year,
                cost_gbp_m=round(total / 1e6, 0),
                households_reached_m=round(reached / 1e6, 2),
            )
            for d in range(1, 11):
                mean = _mean_cell(
                    by_decile[d], lambda h, i=r.id: _measure_gain(i, h)[1]
                )
                decile_impact.append({
                    "measure_id": r.id, "decile": d, "year": year,
                    "avg_change_gbp": _cell(mean),
                })
        measures.append(entry)

    return {
        "meta": {
            "placeholder": True,
            "notice": (
                "Pre-release template: every figure on this page comes from "
                "synthetic households and placeholder settings. It is not an "
                "estimate of the January to March 2027 cap or its effects."
            ),
            "title": "Energy price cap, January to March 2027",
            "event_quarter": years.EVENT_QUARTER,
            "source": "synthetic",
            "template_date": TEMPLATE_DATE,
            "engine": {
                "policyengine_uk": "not run (placeholder)",
                "dataset": "none (synthetic households)",
                "validated": False,
            },
            "basis": years.BASIS,
            "years": [
                {"year": y, "label": years.fiscal_label(y)}
                for y in years.POLICY_YEARS
            ],
            "default_scenario": "central",
            "disclosure_floor": publication.DISCLOSURE_FLOOR,
        },
        "cap": {
            "current_period": cap.CURRENT_PERIOD,
            "history": cap.consistent_history(),
            "payment_methods": cap.CAP["payment_methods"],
            "rates": cap.current_rates(),
            "scenarios": [
                {**row, "change_pct": round(
                    100 * (cap.price_factor(row["id"]) - 1), 1)}
                for row in cap.CAP["scenarios_2027q1"]
            ],
            "sources": cap.CAP["sources"],
        },
        "measures": measures,
        "bills": {"by_decile": bills_by_decile, "by_group": bills_by_group},
        "decile_impact": decile_impact,
        "households": household.all_presets(),
    }


def build_model(**_kwargs) -> dict:
    """Microcosm run through policyengine-uk (the day).

    Steps, once issue #1 is closed: load the frozen engine and dataset
    (G0 record); for each scenario, apply ``cap_q1_2027`` with the growth
    for Ofgem's level; read ``electricity_consumption`` and
    ``gas_consumption`` (household, 2026) under baseline and reform; for
    each computable support measure, read the change in the chosen income
    measure (issue #5); aggregate with the disclosure floor, as in
    ``build_placeholder``.
    """
    raise NotImplementedError(
        "The model run is not wired: no certified Microcosm build pairs "
        "with policyengine-uk 2.175 (issue #1). Use --source placeholder."
    )


def generate(out: Path, source: str = "placeholder") -> dict:
    results = build_placeholder() if source == "placeholder" else build_model()
    publication.check(results)
    publication.write_json(out, results)
    return results
