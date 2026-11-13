import json
from pathlib import Path

from uk_energy_price_cap import cli


def test_freeze_fails_when_the_dataset_is_missing(tmp_path, capsys):
    missing = tmp_path / "microcosm-uk-2024-25-abcd1234" / "missing.h5"
    assert cli.main(["freeze", "--dataset", str(missing)]) != 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "no such dataset file" in captured.err


def test_freeze_fails_when_no_dataset_is_named(capsys):
    assert cli.main(["freeze"]) != 0
    assert "--dataset" in capsys.readouterr().err


def test_freeze_records_the_sha_of_a_present_dataset(tmp_path, capsys):
    dataset = tmp_path / "data.h5"
    dataset.write_bytes(b"not really hdf5")
    assert cli.main(["freeze", "--dataset", str(dataset)]) == 0
    record = json.loads(capsys.readouterr().out)
    assert record["dataset"]["path"] == "data.h5"
    assert len(record["dataset"]["sha256"]) == 64
    assert record["label"]
    # Not the build's file: named as a problem, so a run would refuse it.
    assert record["dataset"]["build"] is None
    assert "dataset_problem" in record


def test_label_names_the_build_and_engine():
    from uk_energy_price_cap.data_build import DATA_BUILD, LABEL

    assert LABEL == (
        f"build {DATA_BUILD.id}, policyengine-uk {DATA_BUILD.engine}, "
        "not in a policyengine.py release"
    )
    assert DATA_BUILD.hf_path == (
        f"releases/microcosm-uk-2024-25-national/{DATA_BUILD.id}/microcosm_uk_2024_25.h5"
    )


def test_model_extra_pins_the_engine_the_build_was_made_on():
    import tomllib

    from uk_energy_price_cap.data_build import DATA_BUILD

    root = Path(__file__).resolve().parents[1]
    pyproject = tomllib.loads((root / "pyproject.toml").read_text())
    model = pyproject["project"]["optional-dependencies"]["model"]
    assert f"policyengine-uk=={DATA_BUILD.engine}" in model
    assert f"policyengine-core=={DATA_BUILD.core}" in model
