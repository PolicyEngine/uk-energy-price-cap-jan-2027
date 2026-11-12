"""Generate ``dashboard/public/data/results.json``.

Two sources, one output schema (docs/RESULTS_SCHEMA.md):

- ``placeholder`` (default, what CI runs): synthetic households built here
  from a fixed seed. No microdata, no model. Every figure is a placeholder
  and the file says so in ``meta``.
- ``model`` (the day): Microcosm through policyengine-uk, unmanaged
  (``model_run.py``). It loads the dataset file directly, not through
  the certified bundle (issue #1), so it runs only with
  ``--allow-unmanaged`` and labels every figure "unvalidated under this
  engine".

Basis (docs/METHOD.md, stated once there): household and decile bill
changes are annualised, a full year at January to March 2027 prices
against a full year at October to December 2026 prices; support costs and
gains are for the fiscal year the measure applies to. The two never share
a chart. Northern Ireland is outside the Ofgem cap and is excluded from
the cap shock; it is shown as its own row.
"""

import json
import random
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from uk_energy_price_cap import cap, household, publication, reforms, years
from uk_energy_price_cap.models import Status

ROOT = Path(__file__).resolve().parents[2]
HOUSEHOLDS_UK = 28_900_000
# Fixed so the committed placeholder file is reproducible byte for byte.
TEMPLATE_DATE = "2026-11-05"
REGIONS = [
    ("NORTH_EAST", "ENGLAND", 0.042),
    ("NORTH_WEST", "ENGLAND", 0.112),
    ("YORKSHIRE", "ENGLAND", 0.083),
    ("EAST_MIDLANDS", "ENGLAND", 0.072),
    ("WEST_MIDLANDS", "ENGLAND", 0.086),
    ("EAST_OF_ENGLAND", "ENGLAND", 0.094),
    ("LONDON", "ENGLAND", 0.124),
    ("SOUTH_EAST", "ENGLAND", 0.138),
    ("SOUTH_WEST", "ENGLAND", 0.088),
    ("WALES", "WALES", 0.049),
    ("SCOTLAND", "SCOTLAND", 0.084),
    ("NORTHERN_IRELAND", "NORTHERN_IRELAND", 0.028),
]
TENURES = [
    ("OWNED_OUTRIGHT", 0.37),
    ("OWNED_WITH_MORTGAGE", 0.26),
    ("RENT_FROM_COUNCIL", 0.09),
    ("RENT_FROM_HA", 0.09),
    ("RENT_PRIVATELY", 0.19),
]
BANDS = [
    ("A", 0.22),
    ("B", 0.19),
    ("C", 0.21),
    ("D", 0.16),
    ("E", 0.10),
    ("F", 0.06),
    ("G", 0.05),
    ("H", 0.01),
    ("I", 0.002),
]
DIMENSIONS = ("region", "tenure", "council_tax_band", "fuel", "payment")


@dataclass
class HouseholdRecord:
    """One household, from the synthetic set or from Microcosm.

    ``electricity`` and ``gas`` are annual spend at October to December
    2026 prices (VAT included); ``current_support`` is current-law energy
    support in 2026-27 (Household Energy Payment, Warm Home Discount,
    Winter Fuel Payment); ``hep`` is the Household Energy Payment alone.
    """

    decile: int
    region: str
    country: str
    tenure: str
    council_tax_band: str
    net_income: float
    electricity: float
    gas: float
    prepayment: bool
    current_support: float
    hep: float
    weight: float
    # Synthetic only: what the placeholder measure gains read.
    qualifying_benefit: bool = False
    disability_benefit: bool = False
    oldest_age: int = 0
    extra: dict = field(default_factory=dict)

    @property
    def fuel(self) -> str:
        return "dual_fuel" if self.gas > 0 else "electric_only"

    @property
    def payment(self) -> str:
        return "prepayment" if self.prepayment else "other"


SyntheticHousehold = HouseholdRecord


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
        income = 9_000 * decile**1.15 * rng.uniform(0.85, 1.15)
        electric_only = rng.random() < 0.16
        electricity = rng.uniform(650, 1_250) * (1.6 if electric_only else 1)
        electricity *= 0.9 + 0.02 * decile
        gas = 0.0 if electric_only else rng.uniform(450, 1_150)
        prepayment = rng.random() < (0.25 if decile <= 3 else 0.08)
        qualifying = rng.random() < max(0.05, 0.6 - 0.07 * decile)
        disability = rng.random() < 0.12
        age = rng.choice([30, 40, 50, 60, 68, 75, 82])
        band = bands[b]
        support = household.support(
            household.Preset(
                "x",
                "x",
                0,
                0,
                "direct_debit",
                country,
                band,
                qualifying,
                age,
                pension_credit=qualifying and age >= 66,
            )
        )
        out.append(
            HouseholdRecord(
                decile=decile,
                region=region,
                country=country,
                tenure=tenures[t],
                council_tax_band=band,
                net_income=round(income, 2),
                electricity=round(electricity, 2),
                gas=round(gas, 2),
                prepayment=prepayment,
                current_support=support["total"],
                hep=support["household_energy_payment"],
                weight=HOUSEHOLDS_UK / n,
                qualifying_benefit=qualifying,
                disability_benefit=disability,
                oldest_age=age,
            )
        )
    return out


FUEL_STRESS_SHARE = 0.10  # energy spend over 10% of net income


def _bill_change(h: HouseholdRecord, factor: float) -> float:
    """Annualised change: a year at the scenario's prices less a year now."""
    if h.country == "NORTHERN_IRELAND":
        return 0.0
    return (h.electricity + h.gas) * (factor - 1)


def _quarter_change(h: HouseholdRecord, factor: float) -> float:
    """The change over January to March 2027 alone, by fuel's Q1 share."""
    if h.country == "NORTHERN_IRELAND":
        return 0.0
    q1 = cap.Q1_CONSUMPTION_SHARE
    return (h.electricity * q1["electricity"] + h.gas * q1["gas"]) * (
        factor - 1
    )


def _measure_gain(measure_id: str, h: HouseholdRecord) -> tuple[int, float]:
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
        return 2027, (
            h.electricity * 0.05 * months
            if h.country != "NORTHERN_IRELAND"
            else 0.0
        )
    if measure_id == "universal_bill_credit":
        return 2026, 150.0 if h.country != "NORTHERN_IRELAND" else 0.0
    if measure_id == "wfp_top_up":
        return 2026, 100.0 if (
            h.oldest_age >= 66 and h.country != "SCOTLAND"
        ) else 0.0
    raise KeyError(measure_id)


def _mean_cell(rows, value, floor=publication.DISCLOSURE_FLOOR):
    records = len(rows)
    weight = sum(h.weight for h in rows)
    if records < floor or weight == 0:
        return None
    return round(sum(value(h) * h.weight for h in rows) / weight, 2)


def _share_cell(rows, test, floor=publication.DISCLOSURE_FLOOR):
    """Percentage of households (weighted) for which ``test`` holds."""
    return _mean_cell(rows, lambda h: 100.0 if test(h) else 0.0, floor)


def _cell(value):
    return {"value": value} if value is not None else {"withheld": True}


def _stressed(h: HouseholdRecord, factor: float) -> bool:
    if h.net_income <= 0:
        return False
    spend = h.electricity + h.gas + _bill_change(h, factor)
    return spend > FUEL_STRESS_SHARE * h.net_income


def assemble(
    hh: list[HouseholdRecord],
    gains: dict[str, tuple[int, list[float]]],
    meta: dict,
) -> dict:
    """The results file from household records and measure gains.

    ``gains`` maps each computable support measure to its policy year and
    one annual gain per household (same order as ``hh``). One function for
    both sources, so the schema cannot drift between them.
    """
    index = {id(h): i for i, h in enumerate(hh)}
    by_decile = defaultdict(list)
    for h in hh:
        by_decile[h.decile].append(h)

    bills_by_decile = []
    bills_by_group = []
    summary = []
    for s in cap.scenario_ids():
        factor = cap.price_factor(s)
        in_cap = [h for h in hh if h.country != "NORTHERN_IRELAND"]
        with_hep = [h for h in hh if h.hep > 0]
        summary.append(
            {
                "scenario_id": s,
                "total_change_gbp_bn": _cell(
                    None
                    if len(hh) < publication.DISCLOSURE_FLOOR
                    else round(
                        sum(_bill_change(h, factor) * h.weight for h in hh)
                        / 1e9,
                        2,
                    )
                ),
                "households_in_cap_m": _cell(
                    round(sum(h.weight for h in in_cap) / 1e6, 2)
                ),
                "avg_change_gbp": _cell(
                    _mean_cell(in_cap, lambda h: _bill_change(h, factor))
                ),
                "energy_over_10pct_now_pct": _cell(
                    _share_cell(hh, lambda h: _stressed(h, 1.0))
                ),
                "energy_over_10pct_then_pct": _cell(
                    _share_cell(hh, lambda h: _stressed(h, factor))
                ),
                "hep_covers_quarter_rise_pct": _cell(
                    _share_cell(
                        with_hep,
                        lambda h: h.hep >= _quarter_change(h, factor),
                    )
                ),
            }
        )
        for d in range(1, 11):
            rows = by_decile[d]
            gross = _mean_cell(rows, lambda h: _bill_change(h, factor))
            share = _mean_cell(
                rows,
                lambda h: (
                    100 * _bill_change(h, factor) / h.net_income
                    if h.net_income > 0
                    else 0.0
                ),
            )
            net = _mean_cell(
                rows, lambda h: _bill_change(h, factor) - h.current_support
            )
            bills_by_decile.append(
                {
                    "scenario_id": s,
                    "decile": d,
                    "gross_change_gbp": _cell(gross),
                    "share_of_net_income_pct": _cell(share),
                    "change_after_support_gbp": _cell(net),
                }
            )
        for dim in DIMENSIONS:
            groups = defaultdict(list)
            for h in hh:
                if dim == "council_tax_band" and (
                    h.country == "NORTHERN_IRELAND"
                ):
                    continue  # NI has domestic rates, not bands (issue #8)
                groups[getattr(h, dim)].append(h)
            for group in sorted(groups):
                bills_by_group.append(
                    {
                        "scenario_id": s,
                        "dimension": dim,
                        "group": group,
                        "outside_cap": group == "NORTHERN_IRELAND",
                        "gross_change_gbp": _cell(
                            _mean_cell(
                                groups[group],
                                lambda h: _bill_change(h, factor),
                            )
                        ),
                    }
                )

    measures = []
    decile_impact = []
    for r in reforms.REFORMS:
        entry = {
            "id": r.id,
            "name": r.name,
            "description": r.description,
            "route": r.route.value,
            "status": r.status.value,
            "lever": r.lever,
            "likelihood": r.likelihood,
            "computable": r.is_computable,
            "reason": r.limit_reason,
            "calculator_only": r.calculator_only,
            "year": None,
            "cost_gbp_m": None,
            "households_reached_m": None,
        }
        withdrawn = r.status == Status.WITHDRAWN
        if r.is_computable and r.lever == "support" and not withdrawn:
            year, values = gains[r.id]
            total = sum(v * h.weight for v, h in zip(values, hh))
            reached = sum(h.weight for v, h in zip(values, hh) if v > 0)
            entry.update(
                year=year,
                cost_gbp_m=round(total / 1e6, 0),
                households_reached_m=round(reached / 1e6, 2),
            )
            for d in range(1, 11):
                mean = _mean_cell(
                    by_decile[d], lambda h, v=values: v[index[id(h)]]
                )
                decile_impact.append(
                    {
                        "measure_id": r.id,
                        "decile": d,
                        "year": year,
                        "avg_change_gbp": _cell(mean),
                    }
                )
        measures.append(entry)

    return {
        "meta": meta,
        "cap": {
            "current_period": cap.CURRENT_PERIOD,
            "history": cap.consistent_history(),
            "payment_methods": cap.CAP["payment_methods"],
            "rates": cap.current_rates(),
            "scenarios": [
                {
                    **row,
                    "change_pct": round(
                        100 * (cap.price_factor(row["id"]) - 1), 1
                    ),
                }
                for row in cap.CAP["scenarios_2027q1"]
            ],
            "sources": cap.CAP["sources"],
        },
        "measures": measures,
        "bills": {
            "summary": summary,
            "by_decile": bills_by_decile,
            "by_group": bills_by_group,
        },
        "decile_impact": decile_impact,
        "official": official_costings(),
        "households": household.all_presets(),
    }


def official_costings() -> list[dict]:
    """Official costings of support already in place (data_inputs/official)."""
    path = ROOT / "data_inputs" / "official" / "costings.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())["costings"]


def _meta(source: str, engine: dict, placeholder: bool, notice: str) -> dict:
    return {
        "placeholder": placeholder,
        "notice": notice,
        "title": "Energy price cap, January to March 2027",
        "event_quarter": years.EVENT_QUARTER,
        "source": source,
        "template_date": TEMPLATE_DATE,
        "engine": engine,
        "basis": years.BASIS,
        "years": [
            {"year": y, "label": years.fiscal_label(y)}
            for y in years.POLICY_YEARS
        ],
        "default_scenario": "central",
        "disclosure_floor": publication.DISCLOSURE_FLOOR,
    }


PLACEHOLDER_NOTICE = (
    "Pre-release template: every figure on this page comes from "
    "synthetic households and placeholder settings. It is not an "
    "estimate of the January to March 2027 cap or its effects."
)


def build_placeholder(n: int = 3000, seed: int = 20270101) -> dict:
    hh = synthetic_households(n, seed)
    gains = {}
    for r in reforms.computable():
        if r.lever != "support":
            continue
        values = [_measure_gain(r.id, h) for h in hh]
        gains[r.id] = (values[0][0], [v for _, v in values])
    engine = {
        "policyengine_uk": "not run (placeholder)",
        "dataset": "none (synthetic households)",
        "validated": False,
    }
    return assemble(
        hh, gains, _meta("synthetic", engine, True, PLACEHOLDER_NOTICE)
    )


def build_model(
    dataset: Path | str | None = None,
    allow_unmanaged: bool = False,
    **_kwargs,
) -> dict:
    """Microcosm through policyengine-uk (model_run.py does the runs)."""
    from uk_energy_price_cap import model_run

    return model_run.build(
        dataset=dataset, allow_unmanaged=allow_unmanaged, assemble=assemble
    )


def generate(
    out: Path,
    source: str = "placeholder",
    dataset: Path | str | None = None,
    allow_unmanaged: bool = False,
) -> dict:
    if source == "placeholder":
        results = build_placeholder()
    else:
        results = build_model(dataset=dataset, allow_unmanaged=allow_unmanaged)
    publication.check(results)
    publication.write_json(out, results)
    publication.write_manifest(out, results)
    return results
