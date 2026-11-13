"""The gas standing-charge route on a small synthetic Microcosm-shaped file.

The real file is a pandas table store: ``household/table`` is one compound
dataset with a field per column. The synthetic file copies that layout.
"""

import h5py
import numpy as np
import pytest

from uk_energy_price_cap import cap, household_kwh, pipeline, reforms

# id, gas_kwh, electricity_kwh, household_weight; file order differs from
# the model's order on purpose, so the join is tested.
ROWS = [
    (30, 0.0, 4_000.0, 2.0),  # electric only, GB
    (10, 5_000.0, 2_500.0, 1.0),  # low gas use, GB
    (40, 10_000.0, 3_000.0, 1.0),  # Northern Ireland, outside the cap
    (20, 15_000.0, 2_700.0, 1.0),  # high gas use, GB
]
COUNTRY = {10: "ENGLAND", 20: "SCOTLAND", 30: "WALES", 40: "NORTHERN_IRELAND"}


def _write(path, rows=ROWS, columns=None):
    dtype = [
        ("index", "<i8"),
        ("household_id", "<i8"),
        ("gas_kwh", "<f8"),
        ("electricity_kwh", "<f8"),
        ("household_weight", "<f8"),
    ]
    if columns is not None:
        dtype = [d for d in dtype if d[0] in columns]
    table = np.zeros(len(rows), dtype=dtype)
    full = [
        "index",
        "household_id",
        "gas_kwh",
        "electricity_kwh",
        "household_weight",
    ]
    for i, row in enumerate(rows):
        values = dict(zip(full, (i, *row)))
        for name, _ in dtype:
            table[i][name] = values[name]
    with h5py.File(path, "w") as f:
        f.create_group("household").create_dataset("table", data=table)
    return path


@pytest.fixture
def h5(tmp_path):
    return _write(tmp_path / "microcosm.h5")


def test_join_follows_the_model_order(h5):
    out = household_kwh.join([20, 10, 30, 40], h5)
    assert out["gas_kwh"] == [15_000.0, 5_000.0, 0.0, 10_000.0]
    assert out["electricity_kwh"] == [2_700.0, 2_500.0, 4_000.0, 3_000.0]


def test_a_household_missing_from_the_file_is_an_error_not_zero(h5):
    with pytest.raises(household_kwh.KwhReadError, match="no kWh row"):
        household_kwh.join([10, 99], h5)


def test_a_file_without_the_kwh_columns_is_an_error(tmp_path):
    path = _write(
        tmp_path / "old.h5",
        columns={"index", "household_id", "household_weight"},
    )
    with pytest.raises(household_kwh.KwhReadError, match="gas_kwh"):
        household_kwh.join([10], path)


def test_standing_charge_moves_into_the_unit_rate_by_hand():
    # 20p a day = £73 a year off each GB gas bill (10 and 20); £146 raised
    # over 20,000 kWh = 0.73p/kWh. Low user: 5,000 x £0.0073 - £73 =
    # -£36.50. High user: 15,000 x £0.0073 - £73 = +£36.50. Electric-only
    # and Northern Ireland homes: unchanged.
    change, rise_p = household_kwh.standing_charge_to_unit_rate(
        kwh=[0.0, 5_000.0, 10_000.0, 15_000.0],
        weights=[2.0, 1.0, 1.0, 1.0],
        in_cap=[True, True, False, True],
        standing_p_per_day=20.0,
    )
    assert rise_p == pytest.approx(0.73)
    assert change == pytest.approx([0.0, -36.5, 0.0, 36.5])


def _records(h5, ids):
    gas = household_kwh.join(ids, h5)["gas_kwh"]
    weights = {r[0]: r[3] for r in ROWS}
    return [
        pipeline.HouseholdRecord(
            decile=1,
            region=COUNTRY[i],
            country=COUNTRY[i],
            tenure="RENT_PRIVATELY",
            council_tax_band="B",
            net_income=20_000.0,
            electricity=900.0,
            gas=0.0,
            prepayment=False,
            current_support=0.0,
            hep=0.0,
            weight=weights[i],
            gas_kwh=g,
        )
        for i, g in zip(ids, gas)
    ]


def test_registered_measure_reads_the_file_per_household(h5):
    ids = [10, 20, 30, 40]
    hh = _records(h5, ids)
    measure = reforms.get("gas_standing_charge_removal")
    assert (
        measure.is_computable and measure.route.value == "dashboard-structural"
    )
    year, gains = measure.household_rule(hh)
    assert year == 2027
    removed = cap.DAYS * cap.current_rates()["gas_standing_p_per_day"] / 100
    rise = 2 * removed / 20_000
    # A gain is the fall in the bill.
    assert gains == pytest.approx(
        [removed - 5_000 * rise, removed - 15_000 * rise, 0.0, 0.0]
    )
    weights = [h.weight for h in hh]
    assert sum(g * w for g, w in zip(gains, weights)) == pytest.approx(0)
