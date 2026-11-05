import json
from pathlib import Path

import pytest

from uk_energy_price_cap import cap, pipeline, publication, reforms

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
    assert [m["id"] for m in results["measures"]] == [r.id for r in reforms.REFORMS]
    for m in results["measures"]:
        if not m["computable"]:
            assert m["cost_gbp_m"] is None
            assert m["reason"]


def test_northern_ireland_is_outside_the_cap(results):
    rows = [r for r in results["bills"]["by_group"]
            if r["group"] == "NORTHERN_IRELAND" and r["scenario_id"] == "central"]
    assert rows and rows[0]["outside_cap"] is True
    assert rows[0]["gross_change_gbp"] == {"value": 0.0}


def test_every_scenario_has_ten_deciles(results):
    for s in cap.scenario_ids():
        rows = [r for r in results["bills"]["by_decile"] if r["scenario_id"] == s]
        assert [r["decile"] for r in rows] == list(range(1, 11))


def test_small_cells_are_withheld(results):
    band_i = [r for r in results["bills"]["by_group"]
              if r["dimension"] == "council_tax_band" and r["group"] == "I"]
    # Band I holds about 0.2% of 3,000 synthetic households: below the floor.
    assert band_i
    assert all(r["gross_change_gbp"] == {"withheld": True} for r in band_i)


def test_model_source_is_not_wired():
    with pytest.raises(NotImplementedError, match="issue #1"):
        pipeline.build_model()
