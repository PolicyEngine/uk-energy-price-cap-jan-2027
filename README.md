# Energy price cap, January to March 2027

PolicyEngine dashboard for the Ofgem energy price cap that covers 1 January to 31 March 2027. Ofgem plans to announce the cap on or before 25 November 2026. The dashboard will show how household energy bills change and how much of the change the energy support already announced offsets.

**Status: pre-release template.** Nothing in this repository is an estimate of the January 2027 cap or its effects. Until Ofgem publishes the cap, every cap level, measure and figure is a placeholder.

## What the dashboard will show

- **The cap**: the typical Direct Debit dual-fuel bill for January to March 2027, the change from October to December 2026 (£1,723), and the levels for Standard Credit, prepayment and Economy 7. The cap history is shown on one typical-consumption basis, with the July 2026 change of basis marked.
- **Household bills**: the average change in household energy spend, in pounds and as a share of net income, by income decile, region, tenure, council tax band, gas or electric-only homes and prepayment or not.
- **Support**: the effect of the £100 Household Energy Payment, the Warm Home Discount, the 0% VAT rate on domestic electricity and the Winter Fuel Payment, and which households receive each.
- **Policy options**: the cost of each support lever and who would gain from it, such as a larger or wider Household Energy Payment, a larger Warm Home Discount, a longer VAT cut, a targeted discount or a credit on every bill.
- **Household examples**: annual bills and support for a set of example households, from Ofgem unit rates and standing charges.
- **Method and data**: what is modelled, what is not, and why.

## Method in brief

The figures will come from PolicyEngine UK, a static microsimulation model of the UK tax and benefit system, run on Microcosm, PolicyEngine's calibrated survey-based dataset. Microcosm holds household spending on electricity and gas in pounds. The model moves that spending with an energy price index, so the cap shock is a change to that index, compared against the forecast path the model uses now. Support measures are changes to model parameters. Results are static: households do not change how much energy they use. Costs are on a fiscal-year basis (April to March) unless a figure says otherwise. Northern Ireland is outside the Ofgem cap and is reported apart. A measure that acts only through something the data do not hold, such as kilowatt-hours or tariff type, is reported as not computable, with the reason, and never as £0.

## Data and model versions

| Component | Version |
|---|---|
| policyengine-uk | 2.175.7 (provisional, unmanaged; 2.170.2 or later holds the Household Energy Payment, the energy price indices and the July 2027 VAT end date) |
| Microcosm | to be fixed at the freeze; no certified build pairs with policyengine-uk 2.175 yet |

These versions are provisional. The certified bundle in policyengine 6.14.0 pins policyengine-uk 2.151.0, which lacks the energy measures above. Until a certified pair exists, every figure is labelled as unvalidated under this engine. The README will record the final engine and data pair used on the day.

## Results

No results yet. The file in `dashboard/public/data/results.json` comes from synthetic households and placeholder settings, and says so in `meta`.

## How to run

```
uv sync --extra dev
uv run pytest
uv run uk-energy-price-cap ledger      # coverage ledger as CSV
uv run uk-energy-price-cap generate    # placeholder results.json
uv run python scripts/check_public_data.py
cd dashboard && bun install && bun run dev
```

A model run needs `uv sync --extra model` and the frozen Microcosm file. No certified engine and data pair exists yet (issue #1), so it runs unmanaged and labels every figure: `uv run uk-energy-price-cap generate --source model --allow-unmanaged --dataset <file>`. `make` has one target per gate (`make freeze`, `make generate`, `make check`, `make build`).

## Layout

| Path | Content |
|---|---|
| `src/uk_energy_price_cap/reforms.py` | Measure registry: every candidate lever, its route and status (all placeholders) |
| `src/uk_energy_price_cap/measure_templates.py` | Parameter-change templates |
| `src/uk_energy_price_cap/cap.py`, `cap_levels.json` | Ofgem levels, rates, scenarios and bill arithmetic |
| `src/uk_energy_price_cap/household.py` | Example households and support rules |
| `src/uk_energy_price_cap/pipeline.py` | Generates `results.json` |
| `src/uk_energy_price_cap/publication.py`, `sign_off.py` | Publication gate and disclosure floor |
| `src/uk_energy_price_cap/data_limits.py`, `model_limits.py` | What the data and the engine cannot carry |
| `data_inputs/` | Expected effects, official figures, drill packet hashes |
| `docs/` | Method, schema, data contract, colours, runbook, drill, candidate reforms, risk register |
| `dashboard/` | Next.js page |

## Licence

[GNU Affero General Public License v3.0](LICENSE), like other PolicyEngine repositories.
