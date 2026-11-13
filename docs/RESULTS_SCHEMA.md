# results.json schema

One file, `dashboard/public/data/results.json`, written by `uk-energy-price-cap generate`. Every field is required and has no default. `publication.validate` and `dashboard/scripts/check-public-files.mjs` check it.

A **cell** is `{"value": number}` or `{"withheld": true}`. A withheld cell carries no number.

| Key | Content |
|---|---|
| `meta.placeholder` | `true` while any measure is a placeholder. The page shows `meta.notice`. |
| `meta.notice` | The text shown above the tabs. |
| `meta.title`, `meta.event_quarter` | Page title; `2027Q1`. |
| `meta.source` | `synthetic` (template) or `model`. |
| `meta.template_date` | Fixed date of the placeholder build, so the file is reproducible. |
| `meta.engine` | `policyengine_uk`, `dataset`, `validated` (bool); a model run adds `policyengine_core`, `policyengine`, `dataset_sha256` and `label` ("build <id>, policyengine-uk <version>, not in a policyengine.py release", from `data_build.LABEL`). |
| `meta.run` | Model run only: `commit`, `clean`, `versions`, `dataset`, `checks`. |
| `meta.basis` | The declared basis (`years.json`). |
| `meta.years` | `[{year, label}]` policy years. |
| `meta.default_scenario`, `meta.disclosure_floor` | Scenario shown first; 10. |
| `cap.current_period` | `2026Q4`. |
| `cap.history` | `[{period, label, direct_debit, tdcv_basis, restated?}]`. |
| `cap.payment_methods` | `{period: {direct_debit, standard_credit, prepayment, economy_7_direct_debit}}`. |
| `cap.rates` | GB average Direct Debit unit rates and standing charges. |
| `cap.scenarios` | `[{id, label, direct_debit, placeholder, change_pct}]`. On the day: one row, Ofgem's level. |
| `cap.sources` | Source line for each block. |
| `measures` | One per registry entry, in registry order: `id, name, description, route, status, lever, likelihood, computable, reason, calculator_only, year, cost_gbp_m, households_reached_m`. `status` is `placeholder`, `announced` or `withdrawn`. A measure that is not computable, or withdrawn, has `cost_gbp_m: null`; one that is not computable has a `reason`. |
| `bills.summary` | `[{scenario_id, total_change_gbp_bn, households_in_cap_m, avg_change_gbp, energy_over_10pct_now_pct, energy_over_10pct_then_pct, hep_covers_quarter_rise_pct}]` (cells). Annualised basis; Northern Ireland excluded from the cap figures. `hep_covers_quarter_rise_pct` is the share of households receiving the Household Energy Payment whose rise over January to March alone (each fuel's January to March share of a year's use) is no more than the payment. |
| `bills.by_decile` | `[{scenario_id, decile, gross_change_gbp, share_of_net_income_pct, change_after_support_gbp}]` (cells). |
| `bills.by_group` | `[{scenario_id, dimension, group, outside_cap, gross_change_gbp}]`; dimensions `region, tenure, council_tax_band, fuel, payment`. Northern Ireland is left out of `council_tax_band` (domestic rates, not bands). |
| `decile_impact` | `[{measure_id, decile, year, avg_change_gbp}]` for each computable support measure. |
| `official` | `[{id, name, year, cost_gbp_bn, source, url}]` from `data_inputs/official/costings.json`: official costings, shown beside PolicyEngine's. |
| `households` | `[{id, label, inputs, bill_oct_dec_2026, bill_jan_mar_2027: {scenario: £}, support}]`; `support` has `household_energy_payment, warm_home_discount, winter_fuel_payment, pension_age_winter_heating_payment, total`. |

`manifest.json`, beside the results, records the results SHA-256 and what made them (`publication.manifest`); `uk-energy-price-cap validate` checks it.
