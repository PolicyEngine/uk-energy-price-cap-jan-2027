# Data contract

What the pipeline reads from Microcosm and the model, and what it must never write.

## Reads (household level unless stated)

| Variable | Use | Status |
|---|---|---|
| `electricity_consumption`, `gas_consumption` | Bill change | In the data (pounds, 2024 prices; `energy_price_basis` = calendar 2024) |
| `household_weight` | Aggregation | In the data; never written to a public file |
| `region`, `country` | Groups; Northern Ireland exclusion | In the data |
| `tenure_type`, `council_tax_band` | Groups; Household Energy Payment | In the data. Northern Ireland households carry bands (issue #8) |
| `uses_energy_prepayment_meter` | Prepayment group | In the data (about 12.5% of households); docstring out of date (issue #8) |
| `household_net_income` or `hbai_household_net_income` | Deciles; gains | Choice open (issue #5) |
| `household_energy_payment`, `warm_home_discount`, `winter_fuel_allowance` | Current support | Model, policyengine-uk 2.175 or later (issue #1) |
| `electricity_consumption_kwh`, `gas_consumption_kwh` | Rate reforms | Not filled (issue #4). The build exports annual `household.electricity_kwh` and `household.gas_kwh` (calendar 2024, from `eeb6093e`); mapping them onto these monthly inputs waits on policyengine-uk#2890 item 1 |

## Writes

`dashboard/public/data/results.json` only (docs/RESULTS_SCHEMA.md). No record identifiers, weights, record counts, area codes or cells below 10 survey households. Microdata files (`.h5` and similar) are never committed (`.gitignore`, `scripts/check_public_data.py`).

## Hugging Face and cloud storage

The dataset comes from the private Microcosm repository on Hugging Face through the cached login. Local-area weight matrices sit in private cloud storage, not on Hugging Face. This dashboard does not use them: national, nation and region only.
