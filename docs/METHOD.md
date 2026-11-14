# Method

Status: pre-release template. This note describes the method planned for the day. Each section marks what is still open, with its issue.

## Engine and data

- PolicyEngine UK, a static microsimulation model of the UK tax and benefit system, on Microcosm, PolicyEngine's calibrated survey-based dataset.
- The energy parameters this dashboard needs, in the form it reads them, exist from policyengine-uk 2.170.2: the energy price indices, the Household Energy Payment and the 1 July 2027 end of the 0% VAT rate on domestic electricity. The Warm Home Discount and the electricity VAT rate exist from 2.165.1, with the pre-Budget VAT end date (`model_limits.MIN_ENGINE`). The pin is policyengine 6.17.2, which pins policyengine-uk 2.174.1 and certifies Microcosm build `microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e` (SHA-256 `0a9b77db1c0dee2693cb2d47bad68da34cb662916eee4829942bcd45de581f25`). That is the certified pair. The pair planned for the day, and used for drill 7, is build `uk-frs-calibration-attempt-20261112T133744Z-6f918b81` with policyengine-uk 2.177.7 (not in a policyengine.py release) (#18).
- A model run is still unmanaged (it loads the frozen file directly, not through the bundle; issue #1): `uk-energy-price-cap generate --source model --allow-unmanaged --dataset <file>`. It records the dataset's SHA-256 and the installed versions in `manifest.json` beside the results, refuses a dirty tree, and labels every figure "unvalidated under this engine". `uk-energy-price-cap freeze --dataset <file>` prints the G0 record.

## Declared basis (stated once)

| Item | Basis |
|---|---|
| Bills | Annualised: a full year at January to March 2027 prices against a full year at October to December 2026 prices. Household, decile and group bill changes, and the headline totals, use this basis. |
| Year | Support costs and gains are for the fiscal year the measure applies to (April to March; model year 2026 is 2026-27). No chart mixes an annualised bill change with a fiscal-year cost. |
| Spend | Household spending, VAT included, cash. A model run restates each household's fiscal 2026-27 spend to October to December 2026 prices with the engine's own price indices, fuel by fuel. |
| Behaviour | Static: households do not change how much energy they use. |
| Support | Gross: the change in the payments a measure acts on (Household Energy Payment, Warm Home Discount, Winter Fuel Payment, bill credit) or in electricity VAT. Winter Fuel Payment recovery through income tax above £35,000 is not netted off. The Warm Home Discount counts as support here although suppliers fund it and `household_net_income` leaves it out (issue #5). |
| Income | Shares of income use `household_net_income`. |
| Spend level | One spending level. Builds from Microcosm main after PolicyEngine/microcosm#1420 set electricity spend to ONS household spending (Consumer Trends, September 2026 edition, 04.5.1). Gas spend stays at DESNZ volumes times DESNZ prices, close to ONS 04.5.2; that line also counts bottled gas, and netting it out is open as PolicyEngine/microcosm#1095. Older builds sit above ONS on both fuels (issue #7). The G0 freeze names the build and its gap, from the build's `calibration_diagnostics.json`. |
| Fuel stress | Energy spend above 10% of net income, a proxy, not the official fuel poverty measure. |

## The cap shock

1. Ofgem publishes the typical Direct Debit dual-fuel bill for January to March 2027 on the 2026 typical-consumption basis (2,500 kWh electricity, 9,500 kWh gas).
2. Bill changes (the annualised basis above) apply the ratio of that level to the October to December 2026 level (£1,723, same basis) to each household's spend. Ofgem's own figures, not the model's price path, set this ratio, so the typical household's change matches Ofgem's.
3. In the model, `gov.economic_assumptions.energy_prices.obr.utilities` is the OBR's CPI utilities inflation, year on year, by calendar quarter: each quarter's index level is the level a year earlier times one plus that rate, with the electricity VAT change taken out. The lever `cap_q1_2027` sets the 2027Q1 rate to `(1 + 0.113241) × (announced cap / £1,875) − 1`, so the 2027Q1 level is the announced cap over the OBR path's cap (EFO para 2.22) times the baseline level. The VAT adjustment is the same in baseline and reform, so it cancels.
4. Because the rate is year on year, a higher 2027Q1 level would carry into 2028Q1. The lever offsets the 2028Q1 rate so that prices return to the OBR path from April 2027 and fiscal 2027-28 is unchanged (the gap between the OBR path and the cap lasts one quarter, as issue #2 frames it). Whether the shock should persist instead is open on the readiness issue (#10). The fiscal 2026-27 spend change this gives is a check at G2, recorded in the manifest, not a chart.
5. Both fuels move together until the model has a rate for each (issue #2).
6. Northern Ireland is outside the Ofgem cap. Its households are excluded from the cap shock, from the council tax band breakdown and from the headline totals, and shown as their own row (issue #8).

Never take a ratio of cap levels across July 2026 without restating both on one basis. `gov.ofgem.energy_price_cap` mixes the two bases (issue #3).

## Support

| Measure | Current law in the model (2026-27) | Parameter |
|---|---|---|
| Household Energy Payment | £100, England, council tax bands A to D | `gov.treasury.household_energy_payment.*` |
| Warm Home Discount | £150, England and Wales; Pension Credit, Universal Credit, Housing Benefit, income-related ESA; receipt 85% and 70%. Scotland runs its own scheme (Core Group 1, Pension Credit Guarantee Credit), which the model does not compute: the household examples include it, national figures do not | `gov.ofgem.warm_home_discount.*` |
| VAT on domestic electricity | 0% in Great Britain from 1 October 2026 to 30 June 2027 | `gov.hmrc.vat.domestic_electricity_rate.great_britain` |
| Winter Fuel Payment | £200 or £300 a household (shared rates where two eligible people live together); recovered above £35,000 taxable income. Not paid in Scotland | `gov.dwp.winter_fuel_payment.*` |
| Pension Age Winter Heating Payment (Scotland) | £211.15 under 80, £316.70 at 80 or over (2026-27) | `gov.social_security_scotland.pawhp.*` |

These measures are already in the baseline. A statement that repeats them is not a new measure.

## What is not computable, and why

The data hold electricity and gas spend in pounds. Builds from `eeb6093e` on also export annual kWh by fuel (calendar 2024), but policyengine-uk's kWh inputs are monthly and are not filled from them until policyengine-uk#2890 item 1. The data hold no tariff or payment method other than a prepayment flag, heating fuel or energy debt. So electricity standing-charge reforms (Economy 7 homes cannot be told apart), per-unit subsidies, rates by region or payment method, and debt relief are not computable (issue #4). The gas standing charge is computable from the file: `gas_kwh > 0` identifies gas households (24.3m on build `6f918b81`, matching gas spend above zero on every row), joined on `household_id`. This branch still pins the certified pair and publishes it as not yet computed; the engine move (#18) computes it. They are published as not computable with the reason, never as £0. The registry (`src/uk_energy_price_cap/reforms.py`) records each reason.

## Market Stabilisation Charge

Ofgem consulted in October 2026 on activating the Market Stabilisation Charge, with a decision due in mid-November. It is a payment between suppliers when a customer switches after a wholesale price fall, and does not change the cap level, so it does not enter these figures.

## Disclosure

The figures rest on UK Data Service survey microdata. No public file carries record identifiers, weights or record counts. A cell resting on fewer than 10 survey households is withheld (`publication.DISCLOSURE_FLOOR`).
