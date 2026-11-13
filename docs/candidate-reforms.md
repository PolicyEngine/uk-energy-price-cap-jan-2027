# Candidate reforms

Probable levers between the 25 November announcement and spring 2027, with the route each takes in this repository. Values in the registry are placeholders from the planning ranges below. Sources: Ofgem, OBR, DESNZ, DWP, HMRC and GOV.UK; supplier and market forecasts only for the planning range.

## The cap itself

| Item | Value | Source |
|---|---|---|
| October to December 2026 | £1,723 (Direct Debit, dual fuel, 2026 basis); Standard Credit £1,861; prepayment £1,678; Economy 7 £1,046 | Ofgem summary letter, 26 August 2026 |
| Forecast path in the model | about £1,875 for January to March 2027 | OBR, Economic and fiscal outlook, October 2026, para 2.22 |
| Planning range | £1,950 to £2,300; central £2,180 (+26%) | Supplier and market forecasts, 30 September to 4 November 2026 |
| Window | wholesale observation 19 August to 17 November 2026; announcement on or before 25 November | Ofgem |

## Levers

| Registry id | Lever | Placeholder | Plausible range | Likelihood | Route | Data or model need |
|---|---|---|---|---|---|---|
| `cap_q1_2027` | The January to March 2027 cap | £2,180 | £1,950 to £2,300 | certain | dashboard-param | policyengine-uk 2.175+ (#1); one rate for both fuels (#2) |
| `hep_top_up` | Larger Household Energy Payment | £200 | £100 to £300; a second payment | medium | dashboard-param | #1 |
| `hep_band_e` | Payment extended to band E | bands A to E | A to E | low | dashboard-param | #1 |
| `hep_great_britain` | Payment in Scotland and Wales | England, Scotland, Wales | reported plans in both nations; official sources not yet confirmed | medium | dashboard-param | #1; band valuations differ by nation |
| `whd_uplift` | Larger Warm Home Discount | £300 | £250 to £400 | medium | dashboard-param | #1; #5 (income measure) |
| `whd_disability_benefits` | Warm Home Discount for disability benefits | add PIP, Attendance Allowance | wider benefit list | low | dashboard-param | #1; #5 |
| `electricity_vat_to_march_2028` | 0% VAT on electricity to March 2028 | to 31 March 2028 | to September 2027 or permanent | medium | dashboard-param | #1 |
| `gas_vat_zero` | 0% VAT on gas | 0% | 0% for some quarters | low | needs-pe-uk-first | #6 |
| `universal_bill_credit` | Credit on every bill | £150 | £100 to £400 | low | dashboard-param | none |
| `wfp_top_up` | Larger Winter Fuel Payment | +£100 | +£50 to +£200 | low | dashboard-param | none |
| `targeted_energy_discount` | Targeted discount | £175 below £24,000 | flat or tiered, about £2bn | medium | needs-pe-uk-first | port existing contributed code into `measures/` |
| `gas_standing_charge_removal` | Gas standing charge into the unit rate | revenue neutral | from 2027; government says about 60% of households save about £45 a year | announced (detail pending) | dashboard-structural (file `gas_kwh`) | #4 |
| `electricity_standing_charge_shift` | Part of the electricity standing charge into the unit rate | 50% | 0 to 100% | low | not-computable | #4 |
| `price_guarantee` | Bills held at a set level | £1,723 | £1,723 to £2,000 | low | needs-pe-uk-first | #3 |
| `levies_off_electricity` | Remaining policy costs off electricity | about £40 to £80 | unconfirmed | low | needs-pe-uk-first | #2 |
| `cold_weather_payment` | Larger Cold Weather Payment | £50 a week | £25 to £50 | low | needs-pe-uk-first | policyengine-uk#435; Scotland pays the Winter Heating Payment |
| `energy_debt_relief` | Energy debt relief | one-off | Ofgem to consult | announced | ledger | no arrears in the data |
| `prepayment_levelisation` | Prepayment levelisation | – | Ofgem policy | low | not-computable | #4 |

## Already in the baseline (not new measures)

- £100 Household Energy Payment, England, bands A to D, 2026-27.
- 0% VAT on domestic electricity in Great Britain, 1 October 2026 to 30 June 2027.
- £150 Warm Home Discount, 2026-27.
- Winter Fuel Payment at £200 and £300, recovered above £35,000.

## Not a cap-day reform, same timeline

- Ofgem's decision on activating the Market Stabilisation Charge, expected mid-November. It does not change the cap level.
- A possible change to the debt-related costs allowance in the cap.
- April 2027 benefit uprating by September 2026 CPI (3.5%).
