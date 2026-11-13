# Model risk register

| # | Risk | Effect on the day | Likelihood | Mitigation | Issue |
|---|---|---|---|---|---|
| 1 | No policyengine.py release covers the pair the run uses (build `uk-frs-calibration-attempt-20261112T133744Z-6f918b81`, policyengine-uk 2.177.7); build `…-6f918b81` will supersede it | Run is unmanaged; every figure carries the build label; figures move when the build changes | medium | The run refuses another SHA-256 or engine version; switch `DATA_BUILD` when 6f918b81 is published | #1 |
| 2 | One growth rate moves electricity and gas together | Fuel split of the change is wrong if Ofgem moves them apart | high | Separate electricity and gas growth, or an Ofgem index by fuel | #2 |
| 3 | Cap parameter mixes typical-consumption bases | About 11% error in any ratio across July 2026; price guarantee mis-scaled | certain if used | Restate on one basis | #3 |
| 4 | No kWh, rates or tariff type | Standing charge, per-unit and payment-method reforms not computable | certain | Export kWh from the data build; add rate parameters | #4 |
| 5 | Warm Home Discount outside `household_net_income` | Decile chart shows no effect from discount reforms | certain if that measure is used | Choose the income measure; check recipients against about 6m | #5 |
| 6 | Gas VAT shares the reduced rate | Gas VAT cut would move other goods | certain if used | Add a gas rate | #6 |
| 7 | Spend above ONS levels (13% electricity, 31% gas) | Support and bill totals high against ONS-based figures | medium | Record the choice; show both levels | #7 |
| 8 | Northern Ireland moved by a GB price index; carries council tax bands | Bill rise and payment applied where the cap does not apply | high | Exclude Northern Ireland in the pipeline | #8 |
| 9 | Annualised against in-quarter figures | Q1 is a winter quarter: in-quarter spend is above a quarter of the year | medium | Declare annualised; show a quarter only with a seasonal profile and its source | – |
| 10 | Static behaviour | Overstates the bill rise where households cut use | low for one quarter | Declared in the basis | – |
| 11 | Economy 7 and prepayment presets use one ratio | Household examples off by a few pounds | medium | Use Annex 9 rates at G3 | – |
| 12 | Late change to the cap's debt allowance or a correction notice | Re-base after G2 | medium | G5 inject process | – |
