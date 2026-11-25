# Ofgem's January 2027 cap: the blog post

The analysis behind PolicyEngine's post on Ofgem's energy price cap for 1 January to 31 March 2027 and what it means for household energy bills in Great Britain, by income decile. It follows the [19 November 2026 post](https://policyengine.org/uk/research/uk-energy-price-cap-january-2027-forecast) on Cornwall Insight's forecast, whose code (`uk-energy-price-cap-2027/run_cap.py`) this folder generalises.

**Status: Ofgem's cap is in.** The `ofgem` block in `inputs.json` holds Ofgem's January to March 2027 rates (announced 25 November 2026), and `results/results-6.20.3.json` holds both Cornwall Insight's forecast and Ofgem's cap. Ofgem publishes no per-fuel typical bills, so the script computes them from its rates; they sum to £2,166.58 against Ofgem's headline of £2,166.

## Files

| File | What it does |
|---|---|
| `inputs.json` | The cap levels: Ofgem's October 2026 rates, Cornwall Insight's forecast, Ofgem's January rates (to fill in), and the cap history for Table 1 and Figure 1 |
| `run_cap.py` | One microsimulation; for each filled January scenario, every figure the post quotes, to `results/results-<policyengine version>.json` |
| `render_post.py` | Fills `template.md` and `meta.json` from the results and writes the article, its `posts.json` entry and its Latest research card into a policyengine-app-v2 checkout |
| `bundles.py` | The certified engine and data pairs the scripts accept |
| `download_data.py` | Fetches the Microcosm UK build the installed `policyengine` certifies |
| `check_reproduction.py` | Checks a 6.20.2 run against the published results of the 19 November post, key by key |
| `check_floor.py` | Prints the survey households behind each published cell (stdout only) |
| `reference/cornwall-post-2026-11-19.json` | The published results of the 19 November post |

## Model and data

| Run | policyengine | policyengine-uk | Microcosm UK build |
|---|---|---|---|
| Ofgem post | 6.20.3 | 2.179.2 | `uk-frs-calibration-attempt-20261122T100732Z-b891aa69` |
| Reproduction of the 19 November post | 6.20.2 | 2.177.7 | `uk-frs-calibration-attempt-20261115T104657Z-fcfac709` |

`pyproject.toml` pins 6.20.3. The scripts refuse any engine that is not one of these certified pairs, and any dataset file whose SHA-256 is not the build's.

## Setup

```bash
cd post
uv sync
HUGGING_FACE_TOKEN=<read token> uv run python download_data.py
```

The dataset is in the private Hugging Face dataset `policyengine/populace-uk-private`. `MICROCOSM_ROOT` (a folder holding `releases/…`) or `MICROCOSM_DATASET` (the file) points the scripts at a copy elsewhere. A national run takes about a minute and several gigabytes of memory; the scripts wait for the shared heavy-run lock, `/tmp/pe-heavy.lock`, if another PolicyEngine run holds it.

## On the day Ofgem announces the cap

1. **Enter Ofgem's numbers** in the `ofgem` block of `inputs.json`, from its announcement, for the Great Britain average, Direct Debit, with VAT (0% on electricity, 5% on gas):
   - `announced_on`: the date as the post should print it, such as `"25 November 2026"`
   - `unit_p_per_kwh`: electricity and gas unit rates, pence per kWh
   - `standing_p_per_day`: electricity and gas standing charges, pence per day
   - `typical_bill_announced`: the headline typical dual-fuel bill, pounds a year (2,500 kWh electricity, 9,500 kWh gas)
   - `typical_bill_by_fuel`: Ofgem's typical bill for each fuel if it gives one; otherwise leave null and the script computes it from the rates

   Also fill `peak_2022` (label, typical bill, basis, source) if Ofgem's announcement compares the January cap with the 2022-23 peak, in Ofgem's terms; otherwise the post keeps a placeholder there.

   The script refuses a partly filled block, and stops if the typical bill from the rates is more than £1.50 from the headline (a typing error, or rates for another payment method or region).
2. **Run the model:**
   ```bash
   uv run python run_cap.py
   uv run python check_floor.py   # every cell should rest on well over 100 survey households
   ```
3. **Render the post** into a policyengine-app-v2 checkout on the post's branch:
   ```bash
   uv run python render_post.py --app-v2 <path to policyengine-app-v2>
   ```
   It prints how many placeholders are left. Three need words, not numbers: the date (from `announced_on`), the link to Ofgem's announcement (Table 1 sources) and the reasons Ofgem gives for the change, attributed to Ofgem in its own wording ("Ofgem attributes the change to …"). Write them into `template.md` and render again. If Ofgem announces on a day other than 25 November, change `date` in `meta.json` too.
4. **Read the rendered post** before publishing. The template is written for a cap that rises; `render_post.py` picks "above" or "below", "more" or "less" and the direction of the standing-charge limitation from the figures, but read every sentence against Ofgem's numbers, particularly if a standing charge falls or one fuel moves the other way.
5. Commit `inputs.json` and `results/results-6.20.3.json` here, and the three files in policyengine-app-v2.

## Dry run on Cornwall Insight's forecast

The scripts reproduce the 19 November post exactly when run on its engine and data:

```bash
MICROCOSM_ROOT=<folder> uv run --no-project --with 'policyengine[uk]==6.20.2' python run_cap.py
uv run python check_reproduction.py results/results-6.20.2.json reference/cornwall-post-2026-11-19.json
uv run python render_post.py --results results/results-6.20.2.json --scenario cornwall --out /tmp/cornwall.md
```

`check_reproduction.py` compares every published figure (Great Britain totals, all ten deciles, the household examples and the inputs). `--scenario cornwall` renders the post's template on the forecast; its tables and chart data match the 19 November post.

`results/results-6.20.3.json` holds the forecast on the Ofgem post's engine and data. The October figures and the forecast's effects move slightly between the two builds; the post's methodology states both.

## Method

As in the 19 November post:

1. Each household's 2026-27 electricity and gas spending in PolicyEngine UK, restated at October to December 2026 prices with the engine's energy price indices (the 2026Q4 level over the fiscal-year level, per fuel).
2. The 5% VAT at which the indices price electricity removed, since domestic electricity in Great Britain carries no VAT from 1 October 2026.
3. Per fuel, the ratio of the January typical bill to the October typical bill (Ofgem's October rates at 2,500 kWh electricity and 9,500 kWh gas) applied to each household's spending.
4. Great Britain only; Northern Ireland is outside the Ofgem cap. Households do not change their use.
5. Results for Great Britain and by income decile (HBAI net income before housing costs, equivalised, person-weighted): average bills before and after, the change, spending as a share of net income, households spending more than 10% of net income on energy, and four household examples from the published rates alone. January to March changes use the engine's quarterly consumption shares (DESNZ Energy Trends) and 90 days of standing charges.

Support (the sections on the Budget's support and the Household Energy Payment): the payment is the engine's `household_energy_payment` for 2026-27, £100 one-off to households in council tax bands A to D in England (the model cannot exclude households where the householder is not responsible for paying council tax, so it overstates recipients slightly). Because the payment is one-off, it is set against the change over January to March, approximated as each household's annual change for each fuel times that fuel's January to March share of a year's use (standing charges included). Both Ofgem caps carry 0% VAT on electricity, so the change already includes the zero rate: the post gives what 5% VAT would add to the change (`vat_on_change`) and, separately, to the October and January electricity bills. Payment reach is reported for England only; the Welsh and Scottish Governments' own £100 payments are not modelled. Government figure quoted: £45 a year average saving from the VAT cut (DESNZ, 28 October 2026).

Limits: the cap covers default tariffs, but the change is applied to every household; the Direct Debit change is applied to every payment method; one factor per fuel misstates the change for households far from typical use when standing charges and unit rates move differently; January rates are held for a full year.
