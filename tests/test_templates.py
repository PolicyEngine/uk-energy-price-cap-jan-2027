import pytest

from uk_energy_price_cap.measure_templates import (
    TemplateError,
    amount_change,
    cap_shock,
    list_change,
    merge,
    quarterly_growth_change,
    rate_change,
)


def test_a_year_stays_a_bare_fiscal_year():
    assert amount_change("gov.a.b", {2026: 200}) == {
        "gov.a.b": {"2026": 200.0}
    }
    assert amount_change("gov.a.b", {"2026": 200}) == {
        "gov.a.b": {"2026": 200.0}
    }
    with pytest.raises(TemplateError):
        amount_change("gov.a.b", {2027: -1})


def test_a_lone_date_is_refused():
    # policyengine-uk reads a lone date as one day of the parameter.
    with pytest.raises(TemplateError, match="one day"):
        amount_change("gov.a.b", {"2026-04-06": 200})
    with pytest.raises(TemplateError):
        amount_change("gov.a.b", {"202٦": 200})


def test_an_interval_is_kept_and_checked():
    out = rate_change("gov.a", {"2027-07-01.2028-03-31": 0})
    assert out == {"gov.a": {"2027-07-01.2028-03-31": 0.0}}
    with pytest.raises(TemplateError, match="ends before"):
        rate_change("gov.a", {"2028-03-31.2027-07-01": 0})
    with pytest.raises(TemplateError):
        rate_change("gov.a", {"2027-13-01.2028-03-31": 0})


def test_rate_change_bounds():
    with pytest.raises(TemplateError):
        rate_change("gov.a", {2027: 1.5})


def test_list_change_rejects_repeats():
    with pytest.raises(TemplateError):
        list_change("gov.a", {2026: ["A", "A"]})


def test_quarterly_growth_keys_one_quarter_each():
    out = quarterly_growth_change("gov.p", {"2027Q1": 0.26, "2028Q4": 0.0})
    assert out == {
        "gov.p": {
            "2027-01-01.2027-03-31": 0.26,
            "2028-10-01.2028-12-31": 0.0,
        }
    }
    with pytest.raises(TemplateError):
        quarterly_growth_change("gov.p", {"2027-01": 0.1})


def test_cap_shock_is_the_gap_to_the_forecast_path():
    # On the forecast path itself nothing moves.
    assert cap_shock(1875, 1875, 0.113241, -0.105705) == (0.113241, -0.105705)
    g, g_next = cap_shock(2180, 1875, 0.113241, -0.105705)
    ratio = 2180 / 1875
    # The quarter's level is ratio times the baseline level ...
    assert (1 + g) / 1.113241 == pytest.approx(ratio, abs=1e-6)
    # ... and the same quarter a year later is back on the baseline:
    # level(q+4) = level(q) (1 + g_next), so the product of the two
    # growth factors matches the baseline's.
    assert (1 + g) * (1 + g_next) == pytest.approx(
        1.113241 * (1 - 0.105705), abs=1e-6
    )
    with pytest.raises(TemplateError):
        cap_shock(0, 1875, 0.1, 0.1)


def test_model_limited_path_refused():
    with pytest.raises(TemplateError, match="issue #6"):
        rate_change("gov.hmrc.vat.domestic_gas_rate", {2027: 0})
    with pytest.raises(TemplateError, match="issue #3"):
        amount_change("gov.ofgem.energy_price_cap", {2027: 2000})


def test_merge_refuses_duplicates():
    a = amount_change("gov.a", {2027: 1})
    with pytest.raises(TemplateError):
        merge(a, amount_change("gov.a", {2027: 2}))
    assert merge(a, amount_change("gov.a", {2028: 2}))["gov.a"]["2028"] == 2
