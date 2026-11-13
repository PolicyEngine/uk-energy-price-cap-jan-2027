import json
from pathlib import Path

import pytest

from uk_energy_price_cap import (
    cap,
    data_build,
    pipeline,
    publication,
    reforms,
)

ROOT = Path(__file__).resolve().parent.parent
COMMITTED = ROOT / "dashboard" / "public" / "data" / "results.json"


@pytest.fixture(scope="module")
def results():
    return pipeline.build_placeholder()


def test_placeholder_passes_the_gate(results):
    assert publication.validate(results) == []
    assert results["meta"]["placeholder"] is True


def test_committed_file_matches_the_generator(results):
    committed = json.loads(COMMITTED.read_text())
    assert committed == json.loads(json.dumps(results))


def test_measures_follow_the_registry(results):
    assert [m["id"] for m in results["measures"]] == [
        r.id for r in reforms.REFORMS
    ]
    for m in results["measures"]:
        if not m["computable"]:
            assert m["cost_gbp_m"] is None
            assert m["reason"]


def test_northern_ireland_is_outside_the_cap(results):
    rows = [
        r
        for r in results["bills"]["by_group"]
        if r["group"] == "NORTHERN_IRELAND" and r["scenario_id"] == "central"
    ]
    assert rows and rows[0]["outside_cap"] is True
    assert rows[0]["gross_change_gbp"] == {"value": 0.0}


def test_every_scenario_has_ten_deciles(results):
    for s in cap.scenario_ids():
        rows = [
            r for r in results["bills"]["by_decile"] if r["scenario_id"] == s
        ]
        assert [r["decile"] for r in rows] == list(range(1, 11))


def test_small_cells_are_withheld(results):
    band_i = [
        r
        for r in results["bills"]["by_group"]
        if r["dimension"] == "council_tax_band" and r["group"] == "I"
    ]
    # Band I holds about 0.2% of 3,000 synthetic households: below the floor.
    assert band_i
    assert all(r["gross_change_gbp"] == {"withheld": True} for r in band_i)


def test_model_run_refuses_without_the_unmanaged_flag():
    from uk_energy_price_cap import model_run

    with pytest.raises(model_run.ModelRunError, match="issue #1"):
        pipeline.build_model()
    with pytest.raises(model_run.ModelRunError, match="--dataset"):
        pipeline.build_model(allow_unmanaged=True)


def _fake_runner(n=40):
    """A stand-in for one simulation: fixed arrays, reform adds £10."""
    regions = ["NORTH_EAST", "SCOTLAND", "WALES", "NORTHERN_IRELAND"]
    countries = ["ENGLAND", "SCOTLAND", "WALES", "NORTHERN_IRELAND"]

    def run(dataset, changes, requests):
        out = {}
        for variable, year in requests:
            if variable == "__index__":
                out[variable] = {
                    "electricity": {"q4": 110.0, "fiscal": 100.0},
                    "gas": {"q4": 100.0, "fiscal": 100.0},
                }
                continue
            values = {
                "household_weight": [100_000.0] * n,
                "household_income_decile": [i % 10 + 1 for i in range(n)],
                "region": [regions[i % 4] for i in range(n)],
                "country": [countries[i % 4] for i in range(n)],
                "tenure_type": ["RENT_PRIVATELY"] * n,
                "council_tax_band": ["B"] * n,
                "uses_energy_prepayment_meter": [0.0] * n,
                "household_net_income": [20000.0] * n,
                "electricity_consumption": [1000.0] * n,
                "gas_consumption": [700.0] * n,
            }.get(variable, [100.0 if changes is None else 110.0] * n)
            out[f"{variable}@{year}"] = values
        return out

    return run


def test_model_run_assembles_the_same_schema():
    from uk_energy_price_cap import model_run

    results = model_run.build(
        dataset="microcosm.h5",
        allow_unmanaged=True,
        assemble=pipeline.assemble,
        runner=_fake_runner(),
    )
    assert publication.validate(results) == []
    assert results["meta"]["source"] == "model"
    assert results["meta"]["engine"]["label"] == data_build.LABEL
    placeholder = pipeline.build_placeholder()
    assert set(results) == set(placeholder)
    assert set(results["bills"]) == set(placeholder["bills"])
    # Spend is restated to October to December 2026 prices per fuel.
    row = next(
        r
        for r in results["bills"]["by_group"]
        if r["dimension"] == "region"
        and r["group"] == "NORTH_EAST"
        and r["scenario_id"] == "central"
    )
    factor = cap.price_factor("central")
    expected = (1000 * 1.1 + 700) * (factor - 1)
    assert row["gross_change_gbp"]["value"] == pytest.approx(expected, 0.01)
    # A gain is the change in gross support; VAT counts down.
    hep = next(m for m in results["measures"] if m["id"] == "whd_uplift")
    # Four support payments, each up £10, for 40 households of 100,000.
    assert hep["cost_gbp_m"] == pytest.approx(160)
    # Drill 7: the VAT lever is withdrawn, so it carries no figure.
    vat = next(
        m
        for m in results["measures"]
        if m["id"] == "electricity_vat_to_march_2028"
    )
    assert vat["cost_gbp_m"] is None


def test_policy_year_reads_the_first_key():
    from uk_energy_price_cap import model_run

    assert model_run.policy_year(reforms.get("hep_top_up")) == 2026
    vat = reforms.get("electricity_vat_to_march_2028")
    assert model_run.policy_year(vat) == 2027


def test_withdrawn_measure_keeps_its_line_without_figures(monkeypatch):
    from uk_energy_price_cap.models import Status

    original = reforms.get("hep_top_up")
    withdrawn = original.model_copy(update={"status": Status.WITHDRAWN})
    monkeypatch.setattr(
        reforms,
        "REFORMS",
        [withdrawn if r.id == "hep_top_up" else r for r in reforms.REFORMS],
    )
    results = pipeline.build_placeholder()
    entry = next(m for m in results["measures"] if m["id"] == "hep_top_up")
    assert entry["status"] == "withdrawn" and entry["cost_gbp_m"] is None
    assert not [
        c for c in results["decile_impact"] if c["measure_id"] == "hep_top_up"
    ]
    assert publication.validate(results) == []


def test_manifest_matches_the_committed_results():
    assert publication.check_manifest(COMMITTED) == []
