import json

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
