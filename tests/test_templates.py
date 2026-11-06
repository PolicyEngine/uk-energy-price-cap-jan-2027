import pytest

from uk_energy_price_cap.measure_templates import (
    TemplateError,
    amount_change,
    growth_for_cap,
    list_change,
    merge,
    quarterly_growth_change,
    rate_change,
)


def test_amount_change():
    assert amount_change("gov.a.b", {2027: 200}) == {
        "gov.a.b": {"2027-01-01": 200.0}
    }
    with pytest.raises(TemplateError):
        amount_change("gov.a.b", {2027: -1})


def test_rate_change_bounds():
    assert rate_change("gov.a", {"2027-07-01": 0})["gov.a"]["2027-07-01"] == 0
    with pytest.raises(TemplateError):
        rate_change("gov.a", {2027: 1.5})


def test_list_change_rejects_repeats():
    with pytest.raises(TemplateError):
        list_change("gov.a", {2026: ["A", "A"]})


def test_quarterly_growth_dates():
    out = quarterly_growth_change("gov.p", {"2027Q1": 0.26, "2027Q2": 0.0})
    assert out == {"gov.p": {"2027-01-01": 0.26, "2027-04-01": 0.0}}
    with pytest.raises(TemplateError):
        quarterly_growth_change("gov.p", {"2027-01": 0.1})


def test_growth_for_cap():
    assert growth_for_cap(1723, 1723) == 0
    assert growth_for_cap(2180, 1723) == pytest.approx(0.265235, abs=1e-6)


def test_model_limited_path_refused():
    with pytest.raises(TemplateError, match="issue #6"):
        rate_change("gov.hmrc.vat.domestic_gas_rate", {2027: 0})
    with pytest.raises(TemplateError, match="issue #3"):
        amount_change("gov.ofgem.energy_price_cap", {2027: 2000})


def test_merge_refuses_duplicates():
    a = amount_change("gov.a", {2027: 1})
    with pytest.raises(TemplateError):
        merge(a, amount_change("gov.a", {2027: 2}))
    assert (
        merge(a, amount_change("gov.a", {2028: 2}))["gov.a"]["2028-01-01"] == 2
    )
