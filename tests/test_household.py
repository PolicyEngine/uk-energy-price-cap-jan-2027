import pytest

from uk_energy_price_cap import cap, household


def test_typical_bill_reproduces_the_october_cap():
    # Ofgem GB average DD rates for Oct-Dec 2026 at 2,500 / 9,500 kWh.
    bill = cap.annual_bill(2500, 9500)
    assert bill["electricity"] == pytest.approx(858.13, abs=0.01)
    assert bill["gas"] == pytest.approx(865.48, abs=0.01)
    assert abs(bill["total"] - cap.current_cap()) < 1


def test_electric_only_pays_no_gas_standing_charge():
    assert cap.annual_bill(3000, 0)["gas"] == 0


def test_rounding_is_half_up_to_the_penny():
    assert cap.pence_to_pounds(1.005) == 1.01
    assert cap.pence_to_pounds(2.675) == 2.68


def test_scenario_scales_the_typical_bill():
    preset = household.BY_ID["typical_dd"]
    then = household.bill(preset, cap.price_factor("central"))["total"]
    assert then == pytest.approx(2180, abs=1.5)


def test_support_rules():
    s = household.support(household.BY_ID["pensioner_couple_band_b"])
    assert s == {"household_energy_payment": 100.0, "warm_home_discount": 150.0,
                 "winter_fuel_payment": 300.0, "total": 550.0}
    assert household.support(household.BY_ID["working_family_band_e"])["total"] == 0
    # Scotland: no £100 under current law, no Warm Home Discount (England and Wales only)
    scot = household.support(household.BY_ID["scotland_band_c"])
    assert scot["household_energy_payment"] == 0
    assert scot["warm_home_discount"] == 0
    assert scot["winter_fuel_payment"] == 200


def test_override_reaches_scotland():
    scot = household.BY_ID["scotland_band_c"]
    out = household.support(
        scot, {"hep_countries": ("ENGLAND", "SCOTLAND", "WALES")})
    assert out["household_energy_payment"] == 100


def test_calculate_shape():
    out = household.calculate("typical_dd", "central")
    assert out["annual_change"] > 0
    assert out["change_after_support"] == pytest.approx(
        out["annual_change"] - out["support"]["total"], abs=0.01)


def test_presets_cover_every_payment_method_shown():
    methods = {p.payment_method for p in household.PRESETS}
    assert methods == {"direct_debit", "prepayment", "economy_7_direct_debit"}
