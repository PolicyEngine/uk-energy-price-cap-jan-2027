"""The model run: Microcosm through policyengine-uk, loaded directly.

The run uses the build in ``data_build.DATA_BUILD`` with the
policyengine-uk version it was built on; no policyengine.py release covers
that pair (issue #1). It loads the dataset file named at the freeze,
refuses a file whose SHA-256 differs from the build's or an installed
policyengine-uk other than the build's, records the installed versions,
and labels every figure with ``data_build.LABEL``. It refuses to start
without ``allow_unmanaged`` or on a dirty tree.

Each simulation runs in its own fresh process (one simulation per
process), so memory is returned between runs; the parent keeps only the
household arrays it needs. A national run is a heavy job: run it alone.

What it reads (household level):
- baseline, fiscal 2026-27: electricity and gas spend, restated to annual
  spend at October to December 2026 prices with the engine's own indices
  (quarterly 2026Q4 over the fiscal-year level, per fuel); net income;
  decile, region, country, tenure, council tax band, prepayment flag; the
  current-law support payments;
- each computable support measure, in its policy year: the change in the
  gross support it acts on (payments up, electricity VAT down), so gains
  are gross of the Winter Fuel Payment charge as the declared basis says;
- the cap lever for each scenario, fiscal 2026-27: the change in
  electricity and gas spend against the OBR path (a check for G2, kept in
  the manifest, not on a chart).
"""

import hashlib
import multiprocessing
from pathlib import Path
from typing import Callable

from uk_energy_price_cap import cap, publication, reforms
from uk_energy_price_cap.data_build import DATA_BUILD, LABEL
from uk_energy_price_cap.model_limits import BUDGET_ERA_ENGINE

YEAR = 2026
HOUSEHOLD = [
    "household_weight",
    "household_income_decile",
    "region",
    "country",
    "tenure_type",
    "council_tax_band",
    "uses_energy_prepayment_meter",
    "household_net_income",
    "electricity_consumption",
    "gas_consumption",
]
SUPPORT = [
    "household_energy_payment",
    "warm_home_discount",
    "winter_fuel_allowance",
    "ebr_energy_bills_credit",
]
# Gains: payments count up, VAT counts down.
GAIN_SIGNS = {**{v: 1.0 for v in SUPPORT}, "domestic_energy_vat": -1.0}
ENERGY = ["electricity_consumption", "gas_consumption"]


class ModelRunError(RuntimeError):
    """The model run cannot start or its output fails a check."""


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version_tuple(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split(".")[:3])


def freeze_record(dataset: Path | str | None = None) -> dict:
    """The G0 freeze record: what a run would use, read from the install."""
    versions = publication.installed_versions()
    record = {
        **publication.git_state(),
        "versions": versions,
        "managed": False,
        "certified": False,
        "label": LABEL,
        "expected": {
            "build": DATA_BUILD.id,
            "sha256": DATA_BUILD.sha256,
            "policyengine-uk": DATA_BUILD.engine,
            "policyengine-core": DATA_BUILD.core,
        },
        "reason": (
            "The run loads the dataset file directly with the "
            "policyengine-uk version the build was made on; no "
            "policyengine.py release covers that pair (issue #1)."
        ),
    }
    uk = versions.get("policyengine-uk")
    if uk and _version_tuple(uk) < _version_tuple(BUDGET_ERA_ENGINE):
        record["engine_problem"] = (
            f"policyengine-uk {uk} predates {BUDGET_ERA_ENGINE}: no "
            "Household Energy Payment or energy price indices"
        )
    elif uk and uk != DATA_BUILD.engine:
        record["engine_problem"] = (
            f"policyengine-uk {uk} is installed, but build "
            f"{DATA_BUILD.id} was made on {DATA_BUILD.engine}: never mix a "
            "build with another engine version"
        )
    if dataset is not None:
        path = Path(dataset).expanduser()
        sha = file_sha256(path) if path.exists() else None
        record["dataset"] = {
            "path": path.name,
            "build": DATA_BUILD.id if sha == DATA_BUILD.sha256 else None,
            "sha256": sha,
        }
        if sha is not None and sha != DATA_BUILD.sha256:
            record["dataset_problem"] = (
                f"{path.name} has SHA-256 {sha}, not that of build "
                f"{DATA_BUILD.id} ({DATA_BUILD.sha256})"
            )
    return record


def _decode(values) -> list:
    import numpy as np

    array = np.asarray(values)
    if array.dtype.kind in "OSU":
        return [
            v.decode() if isinstance(v, bytes) else str(v)
            for v in array.tolist()
        ]
    return array.astype(float).tolist()


def simulate(dataset: str, changes: dict | None, requests: list) -> dict:
    """One simulation (run in a fresh process): variables and indices.

    ``requests`` is a list of ``(variable, year)``; the result maps
    ``"variable@year"`` to a list over households. ``"__index__"`` returns
    the energy price indices needed to restate spend to 2026Q4 prices.
    """
    from policyengine_uk import Microsimulation

    sim = Microsimulation(dataset=dataset, reform=changes or None)
    out = {}
    for variable, year in requests:
        if variable == "__index__":
            p = sim.tax_benefit_system.parameters
            prices = p.gov.economic_assumptions.energy_prices
            out["__index__"] = {
                fuel: {
                    "q4": float(getattr(prices.quarterly, fuel)("2026-10-01")),
                    "fiscal": float(
                        getattr(prices.fiscal_year, fuel)(f"{year}-01-01")
                    ),
                }
                for fuel in ("electricity", "gas")
            }
            continue
        values = sim.calculate(variable, year, map_to="household")
        out[f"{variable}@{year}"] = _decode(values.values)
    return out


def _run(dataset: str, changes: dict | None, requests: list) -> dict:
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(1, maxtasksperchild=1) as pool:
        return pool.apply(simulate, (dataset, changes, requests))


def policy_year(reform) -> int:
    """The fiscal year a support lever applies to, from its first key."""
    key = next(iter(next(iter(reform.parameter_changes.values()))))
    if "." not in key:
        return int(key)
    year, month = int(key[:4]), int(key[5:7])
    return year if month >= 4 else year - 1


def _gain_variables(reform) -> list[str]:
    if reform.id == "electricity_vat_to_march_2028":
        return ["domestic_energy_vat"]
    return SUPPORT


def build(
    dataset: Path | str | None,
    allow_unmanaged: bool,
    assemble: Callable,
    runner: Callable = _run,
) -> dict:
    """Run the model and assemble the results file (pipeline.assemble)."""
    from uk_energy_price_cap import pipeline

    if not allow_unmanaged:
        raise ModelRunError(
            "No policyengine.py release covers the engine and data pair "
            "(issue #1). Pass --allow-unmanaged to run on the frozen pair; "
            f'every figure is then labelled "{LABEL}".'
        )
    if dataset is None:
        raise ModelRunError("Name the frozen dataset file with --dataset.")
    path = Path(dataset).expanduser()
    if runner is _run and not path.exists():
        raise ModelRunError(f"{path}: no such dataset file")
    record = freeze_record(path if path.exists() else None)
    if runner is _run and record.get("clean") is not True:
        raise ModelRunError(
            "The working tree has uncommitted changes: commit first, so the "
            "manifest names the code that made the figures."
        )
    if record.get("engine_problem"):
        raise ModelRunError(record["engine_problem"])
    if record.get("dataset_problem"):
        raise ModelRunError(record["dataset_problem"])

    support_measures = [
        r
        for r in reforms.computable()
        if r.lever == "support" and r.status.value != "withdrawn"
    ]
    years_needed = sorted({YEAR} | {policy_year(r) for r in support_measures})
    base_requests = [(v, YEAR) for v in HOUSEHOLD] + [("__index__", YEAR)]
    base_requests += [
        (v, y) for y in years_needed for v in SUPPORT + ["domestic_energy_vat"]
    ]
    base = runner(str(path), None, base_requests)
    n = len(base[f"household_weight@{YEAR}"])
    index = base["__index__"]
    to_q4 = {
        fuel: index[fuel]["q4"] / index[fuel]["fiscal"]
        for fuel in ("electricity", "gas")
    }

    def col(name, year=YEAR):
        return base[f"{name}@{year}"]

    hh = []
    for i in range(n):
        hep = col("household_energy_payment")[i]
        current = (
            hep
            + col("warm_home_discount")[i]
            + col("winter_fuel_allowance")[i]
        )
        decile = int(col("household_income_decile")[i])
        hh.append(
            pipeline.HouseholdRecord(
                decile=min(max(decile, 1), 10),
                region=col("region")[i],
                country=col("country")[i],
                tenure=col("tenure_type")[i],
                council_tax_band=col("council_tax_band")[i],
                net_income=col("household_net_income")[i],
                electricity=col("electricity_consumption")[i]
                * to_q4["electricity"],
                gas=col("gas_consumption")[i] * to_q4["gas"],
                prepayment=bool(col("uses_energy_prepayment_meter")[i]),
                current_support=current,
                hep=hep,
                weight=col("household_weight")[i],
            )
        )

    gains = {}
    for r in support_measures:
        year = policy_year(r)
        variables = _gain_variables(r)
        reformed = runner(
            str(path), r.parameter_changes, [(v, year) for v in variables]
        )
        values = [0.0] * n
        for v in variables:
            sign = GAIN_SIGNS[v]
            after = reformed[f"{v}@{year}"]
            before = base[f"{v}@{year}"]
            for i in range(n):
                values[i] += sign * (after[i] - before[i])
        gains[r.id] = (year, values)

    checks = {}
    weights = col("household_weight")
    spend_before = [
        col("electricity_consumption")[i] + col("gas_consumption")[i]
        for i in range(n)
    ]
    for s in cap.scenario_ids():
        changes = reforms.cap_q1_2027_changes(cap.scenario(s)["direct_debit"])
        reformed = runner(str(path), changes, [(v, YEAR) for v in ENERGY])
        total = sum(
            (
                reformed[f"electricity_consumption@{YEAR}"][i]
                + reformed[f"gas_consumption@{YEAR}"][i]
                - spend_before[i]
            )
            * weights[i]
            for i in range(n)
        )
        checks[s] = round(total / 1e9, 3)

    engine = {
        "policyengine_uk": record["versions"].get("policyengine-uk"),
        "policyengine_core": record["versions"].get("policyengine-core"),
        "policyengine": record["versions"].get("policyengine"),
        "dataset": (record.get("dataset") or {}).get("build") or path.name,
        "dataset_sha256": (record.get("dataset") or {}).get("sha256"),
        "validated": False,
        "label": LABEL,
    }
    any_placeholder = any(r.is_placeholder for r in reforms.REFORMS)
    meta = pipeline._meta(
        "model",
        engine,
        any_placeholder,
        pipeline.PLACEHOLDER_NOTICE
        if any_placeholder
        else f"Figures from {LABEL}: see Methodology.",
    )
    meta["run"] = {
        "commit": record.get("commit"),
        "clean": record.get("clean"),
        "versions": record["versions"],
        "dataset": record.get("dataset"),
        "checks": {"cap_lever_fiscal_2026_27_gbp_bn": checks},
    }
    return assemble(hh, gains, meta)
