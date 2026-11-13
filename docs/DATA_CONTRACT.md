# Data contract

What the pipeline reads from Microcosm and the model, and what it must never write.

## Reads (household level unless stated)

| Variable | Use | Status |
|---|---|---|
| `electricity_consumption`, `gas_consumption` | Bill change | In the data (pounds, 2024 prices; `energy_price_basis` = calendar 2024) |
| `household_weight` | Aggregation | In the data; never written to a public file |
| `region`, `country` | Groups; Northern Ireland exclusion | In the data |
| `household_id` | Join to the file's kWh columns | In the data; never written to a public file |
| `tenure_type`, `council_tax_band` | Groups; Household Energy Payment | In the data. Scotland and Wales band counts are calibration targets and land within 0.5% (María Juaristi, 13 November 2026). Northern Ireland households carry bands (issue #8) |
| `uses_energy_prepayment_meter` | Prepayment group | In the data (12.6% of households weighted, build 6f918b81); docstring out of date (issue #8); payment method beyond prepayment is issue #19 |
| `household_net_income` or `hbai_household_net_income` | Deciles; gains | Choice open (issue #5) |
| `household_energy_payment`, `warm_home_discount`, `winter_fuel_allowance` | Current support | Model, policyengine-uk 2.175 or later (issue #1) |
| `gas_kwh`, `electricity_kwh` (file columns, calendar 2024) | Gas households and the gas standing-charge route | In the file as household export columns, not exposed by policyengine-uk. `household_kwh.py` reads them with h5py from `household/table` and joins on `household_id`; a household with no row is an error, never 0. `gas_kwh > 0` matches `gas_consumption > 0` on every row: 24.34m households weighted (84.0%, UK incl. Northern Ireland) on build 6f918b81, in line with DESNZ's 84% on gas |
| `electricity_consumption_kwh`, `gas_consumption_kwh` (engine inputs) | Engine rate reforms | Not filled until policyengine-uk#2890 item 1 (issue #4) |

## Writes

`dashboard/public/data/results.json` only (docs/RESULTS_SCHEMA.md). No record identifiers, weights, record counts, area codes or cells below 10 survey households. Microdata files (`.h5` and similar) are never committed (`.gitignore`, `scripts/check_public_data.py`).

## Hugging Face and cloud storage

The dataset comes from the private Microcosm repository on Hugging Face through the cached login. Local-area weight matrices sit in private cloud storage, not on Hugging Face. This dashboard does not use them: national, nation and region only.
