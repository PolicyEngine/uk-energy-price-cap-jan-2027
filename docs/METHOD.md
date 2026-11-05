# Method

Status: pre-release template. This note describes the method planned for the day. Each section marks what is still open, with its issue.

## Engine and data

- PolicyEngine UK, a static microsimulation model of the UK tax and benefit system, on Microcosm, PolicyEngine's calibrated survey-based dataset.
- The energy parameters this dashboard needs exist only in policyengine-uk 2.175 or later: the energy price index, the Household Energy Payment, the Warm Home Discount and the VAT rate on domestic electricity. The certified bundle in policyengine 6.14.0 pins policyengine-uk 2.151.0. No certified Microcosm build pairs with 2.175 yet (issue #1).
- The G0 freeze record names the engine and the dataset, with its SHA-256. If the pair is not certified, every figure carries the label "unvalidated under this engine".

## Declared basis (stated once)

| Item | Basis |
|---|---|
| Year | Fiscal (April to March). Model year 2026 is 2026-27. |
| Bills | Household spending, VAT included, cash. Bill changes are annualised: a full year at January to March 2027 prices. |
| Behaviour | Static: households do not change how much energy they use. |
| Support | Gross. Winter Fuel Payment recovery through income tax above £35,000 is shown apart. |
| Income | To be fixed (issue #5): the Warm Home Discount counts in `hbai_household_net_income` but not in `household_net_income`. |
| Spend level | Microcosm sets electricity and gas spend at DESNZ volumes times DESNZ prices, 13% (electricity) and 31% (gas) above ONS household spending (issue #7). |

## The cap shock

1. Ofgem publishes the typical Direct Debit dual-fuel bill for January to March 2027 on the 2026 typical-consumption basis (2,500 kWh electricity, 9,500 kWh gas).
2. The change from October to December 2026 (£1,723, same basis) sets the quarterly growth in `gov.economic_assumptions.energy_prices.obr.utilities` for 2027Q1, in place of the OBR's path (0.113, a cap of about £1,875).
3. The model moves each household's `electricity_consumption` and `gas_consumption` by that growth. Both fuels move together until the model has a rate for each (issue #2).
4. The bill change is the difference in spend between the reform and the baseline. A price rise changes no income variable, so the pipeline computes it directly.
5. Northern Ireland is outside the Ofgem cap. Its households are excluded from the cap shock and shown as their own row (issue #8).

Never take a ratio of cap levels across July 2026 without restating both on one basis. `gov.ofgem.energy_price_cap` mixes the two bases (issue #3).

## Support

| Measure | Current law in the model (2026-27) | Parameter |
|---|---|---|
| Household Energy Payment | £100, England, council tax bands A to D | `gov.treasury.household_energy_payment.*` |
| Warm Home Discount | £150, England and Wales; Pension Credit, Universal Credit, Housing Benefit, income-related ESA; receipt 85% and 70% | `gov.ofgem.warm_home_discount.*` |
| VAT on domestic electricity | 0% in Great Britain from 1 October 2026 to 30 June 2027 | `gov.hmrc.vat.domestic_electricity_rate.great_britain` |
| Winter Fuel Payment | £200 or £300; recovered above £35,000 taxable income | `gov.dwp.winter_fuel_payment.*` |

These measures are already in the baseline. A statement that repeats them is not a new measure.

## What is not computable, and why

The data hold electricity and gas spend in pounds. They hold no kilowatt-hours, tariff or payment method other than a prepayment flag, heating fuel, mains gas flag or energy debt. So standing-charge reforms, per-unit subsidies, rates by region or payment method, and debt relief are not computable (issue #4). They are published as not computable with the reason, never as £0. The registry (`src/uk_energy_price_cap/reforms.py`) records each reason.

## Disclosure

The figures rest on UK Data Service survey microdata. No public file carries record identifiers, weights or record counts. A cell resting on fewer than 10 survey households is withheld (`publication.DISCLOSURE_FLOOR`).
