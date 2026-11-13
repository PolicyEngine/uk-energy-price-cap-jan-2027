import pytest

from uk_energy_price_cap import reforms
from uk_energy_price_cap.data_limits import DATA_LIMITS
from uk_energy_price_cap.model_limits import (
    model_limit_reason,
    needs_newer_engine,
)
from uk_energy_price_cap.models import Reform, Route, Status


def test_ids_unique():
    ids = [r.id for r in reforms.REFORMS]
    assert len(ids) == len(set(ids))


def test_every_entry_is_a_placeholder_before_the_event():
    assert all(r.status == Status.PLACEHOLDER for r in reforms.REFORMS)
    assert all(
        r.description.startswith("Placeholder.") for r in reforms.REFORMS
    )


def test_not_computable_entries_have_reasons_and_no_changes():
    for r in reforms.REFORMS:
        if not r.is_computable:
            assert r.limit_reason
            assert r.parameter_changes is None


def test_computable_entries_avoid_limited_paths():
    for r in reforms.computable():
        for path in r.parameter_paths():
            assert model_limit_reason(path) is None, path
            assert path not in DATA_LIMITS


def test_energy_paths_need_the_newer_engine():
    # The Budget-era baseline needs 2.170.2 (model_limits.MIN_ENGINE);
    # The model run uses 2.177.7 (data_build.DATA_BUILD), which has it.
    assert needs_newer_engine(reforms.ENERGY_PRICE_PATH) == "2.170.2"
    assert needs_newer_engine(reforms.ELEC_VAT_GB) == "2.165.1"


def test_cap_reform_moves_one_quarter_to_the_placeholder_level():
    change = reforms.get("cap_q1_2027").parameter_changes
    rates = change[reforms.ENERGY_PRICE_PATH]
    assert set(rates) == {"2027-01-01.2027-03-31", "2028-01-01.2028-03-31"}
    ratio = reforms.PLACEHOLDER_Q1_CAP / reforms.OBR_Q1_2027_CAP
    q1 = 1 + rates["2027-01-01.2027-03-31"]
    assert q1 / (1 + reforms.OBR_UTILITIES["2027Q1"]) == pytest.approx(
        ratio, abs=1e-6
    )
    q1_next = 1 + rates["2028-01-01.2028-03-31"]
    assert q1_next * ratio == pytest.approx(
        1 + reforms.OBR_UTILITIES["2028Q1"], abs=1e-6
    )


def test_every_registered_key_is_a_bare_year_or_an_interval():
    import re

    form = re.compile(r"[1-9][0-9]{3}|\d{4}-\d{2}-\d{2}\.\d{4}-\d{2}-\d{2}")
    for r in reforms.REFORMS:
        for path, values in (r.parameter_changes or {}).items():
            for key in values:
                assert form.fullmatch(key), (r.id, path, key)


def test_route_validation():
    with pytest.raises(ValueError):
        Reform(
            id="x",
            name="x",
            route=Route.DASHBOARD_PARAM,
            status=Status.PLACEHOLDER,
            lever="support",
            likelihood="low",
        )
    with pytest.raises(ValueError):
        Reform(
            id="x",
            name="x",
            route=Route.NOT_COMPUTABLE,
            status=Status.PLACEHOLDER,
            lever="support",
            likelihood="low",
        )


def test_ledger_has_one_line_per_measure():
    rows = reforms.ledger_rows()
    assert [r["id"] for r in rows] == [r.id for r in reforms.REFORMS]
    assert {r["route"] for r in rows} <= {route.value for route in Route}
