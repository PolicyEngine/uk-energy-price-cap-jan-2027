from uk_energy_price_cap import years


def test_years():
    assert years.BASE_YEAR == 2026
    assert years.POLICY_YEARS == (2026, 2027)
    assert years.fiscal_label(2026) == "2026-27"
    assert set(years.BASIS) == {"bills", "year", "flow", "behaviour", "support"}
