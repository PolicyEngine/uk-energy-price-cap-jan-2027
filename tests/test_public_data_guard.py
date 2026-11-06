import copy
import json
from pathlib import Path

import pytest

from uk_energy_price_cap import pipeline, publication

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def results():
    return pipeline.build_placeholder()


def test_floor():
    assert publication.apply_floor(5.0, 9) is None
    assert publication.apply_floor(5.0, 10) == 5.0


@pytest.mark.parametrize(
    "key", ["household_weight", "household_id", "weight", "n_records"]
)
def test_identifiers_and_weights_refused(results, key):
    bad = copy.deepcopy(results)
    bad["bills"]["by_decile"][0][key] = 1
    assert publication.validate(bad)


def test_area_codes_refused(results):
    bad = copy.deepcopy(results)
    bad["bills"]["by_group"][0]["group"] = "E14001234"
    assert any("area code" in p for p in publication.validate(bad))


def test_withheld_cell_with_value_refused(results):
    bad = copy.deepcopy(results)
    bad["bills"]["by_decile"][0]["gross_change_gbp"] = {
        "withheld": True,
        "value": 3.0,
    }
    assert publication.validate(bad)


def test_placeholder_flag_cannot_be_dropped(results):
    bad = copy.deepcopy(results)
    bad["meta"]["placeholder"] = False
    assert publication.validate(bad)


def test_cost_on_not_computable_refused(results):
    bad = copy.deepcopy(results)
    m = next(m for m in bad["measures"] if not m["computable"])
    m["cost_gbp_m"] = 0
    assert publication.validate(bad)


def test_public_folder_is_clean():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "check_public_data", ROOT / "scripts" / "check_public_data.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.check() == []


def test_no_microdata_committed():
    tracked = [p for p in ROOT.rglob("*.h5") if ".venv" not in p.parts]
    assert tracked == []
    json.loads(
        (ROOT / "src" / "uk_energy_price_cap" / "cap_levels.json").read_text()
    )
