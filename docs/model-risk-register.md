# Model risk register

| # | Risk | Effect on the day | Likelihood | Mitigation | Issue |
|---|---|---|---|---|---|
| 1 | The model run loads the dataset file directly, not through the certified bundle (policyengine 6.17.2, policyengine-uk 2.174.1, `microcosm-uk-2024-25-national-20261107T020434Z-eeb6093e`) | Run is unmanaged; every figure labelled | medium | Freeze the certified file and check its SHA-256 at G0, or move the run onto the bundle | #1 |
| 2 | One growth rate moves electricity and gas together | Fuel split of the change is wrong if Ofgem moves them apart | high | Separate electricity and gas growth, or an Ofgem index by fuel | #2 |
| 3 | Cap parameter mixes typical-consumption bases | About 11% error in any ratio across July 2026; price guarantee mis-scaled | certain if used | Restate on one basis | #3 |
| 4 | kWh exported by the build but not mapped onto the model's monthly inputs; no rates or tariff type | Standing charge, per-unit and payment-method reforms not computable | certain | kWh inputs, mains gas flag and rate parameters (policyengine-uk#2890 item 1), then map the build's kWh columns; agree the payment-method input | #4 |
| 5 | Warm Home Discount outside `household_net_income` | Decile chart shows no effect from discount reforms | certain if that measure is used | Choose the income measure; check recipients against about 6m | #5 |
| 6 | Gas VAT shares the reduced rate | Gas VAT cut would move other goods | certain if used | Add a gas rate | #6 |
| 7 | Spend above ONS levels (13% electricity, 31% gas) | Support and bill totals high against ONS-based figures | medium | Record the choice; show both levels | #7 |
| 8 | Northern Ireland moved by a GB price index; carries council tax bands | Bill rise and payment applied where the cap does not apply | high | Exclude Northern Ireland in the pipeline | #8 |
| 9 | Annualised against in-quarter figures | Q1 is a winter quarter: in-quarter spend is above a quarter of the year | medium | Declare annualised; show a quarter only with a seasonal profile and its source | – |
| 10 | Static behaviour | Overstates the bill rise where households cut use | low for one quarter | Declared in the basis | – |
| 11 | Economy 7 and prepayment presets use one ratio | Household examples off by a few pounds | medium | Use Annex 9 rates at G3 | – |
| 12 | Late change to the cap's debt allowance or a correction notice | Re-base after G2 | medium | G5 inject process | – |
