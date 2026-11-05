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
    assert all(r.description.startswith("Placeholder.") for r in reforms.REFORMS)


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
    # policyengine 6.14.0 pins policyengine-uk 2.151.0 (issue #1)
    assert needs_newer_engine(reforms.ENERGY_PRICE_PATH) == "2.175.0"


def test_cap_reform_growth_matches_placeholder_level():
    change = reforms.get("cap_q1_2027").parameter_changes
    growth = change[reforms.ENERGY_PRICE_PATH]["2027-01-01"]
    assert growth == pytest.approx(2180 / 1723 - 1, abs=1e-6)


def test_route_validation():
    with pytest.raises(ValueError):
        Reform(id="x", name="x", route=Route.DASHBOARD_PARAM,
               status=Status.PLACEHOLDER, lever="support", likelihood="low")
    with pytest.raises(ValueError):
        Reform(id="x", name="x", route=Route.NOT_COMPUTABLE,
               status=Status.PLACEHOLDER, lever="support", likelihood="low")


def test_ledger_has_one_line_per_measure():
    rows = reforms.ledger_rows()
    assert [r["id"] for r in rows] == [r.id for r in reforms.REFORMS]
    assert {r["route"] for r in rows} <= {route.value for route in Route}
