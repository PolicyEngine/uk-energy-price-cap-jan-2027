On {{ofgem_date}}, Ofgem [announced](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-january-and-31-march-2027) the energy price cap for 1 January to 31 March 2027: {{jan_total:gbp}} a year for a household with typical consumption paying by Direct Debit, a change of {{jan_change:sgbp}} ({{jan_change_pct:spct1}}) from the [current cap](https://www.ofgem.gov.uk/your-energy-supply/your-energy-bill/energy-price-cap-unit-rates-and-standing-charges) of {{oct_total:gbp}}. The consultancy Cornwall Insight had forecast {{fc_total:gbp}} on 18 November; {{vs_fc_sentence}}

Using [PolicyEngine UK](https://policyengine.org/uk), we estimate what Ofgem's cap means for household energy bills across the income distribution in Great Britain. Our [earlier post](https://policyengine.org/uk/research/uk-energy-price-cap-january-2027-forecast) estimated the effects of Cornwall Insight's forecast; this post uses Ofgem's announced rates, and the last section compares the two.

Key results under Ofgem's cap (annual rates unless stated, Great Britain):

- A household with typical consumption sees its bill change by {{ex_typ_change:sgbp}} a year at the January rates ({{ex_typ_change_pct:spct1}}), or about {{ex_typ_q1_change:sgbp}} over January to March
- The average household in Great Britain spends {{mean_after:gbp}} a year on electricity and gas at the January rates, against {{mean_before:gbp}} at October rates (a change of {{mean_change:sgbp}})
- Bills in the bottom income decile change by an average of {{d1_change:sgbp}} a year, and households' energy spending goes from {{d1_share_before:pct1}} to {{d1_share_after:pct1}} of their net income; in the top decile, bills change by an average of {{d10_change:sgbp}}, and households' energy spending goes from {{d10_share_before:pct1}} to {{d10_share_after:pct1}} of their net income
- The number of households spending more than 10% of their net income on energy goes from {{over10_before:m1}} to {{over10_after:m1}}
- On Cornwall Insight's forecast, the same model gives an average change of {{fc_mean_change:sgbp}} a year, against {{mean_change:sgbp}} under Ofgem's cap

## The cap

Ofgem caps the unit rate and the daily standing charge that suppliers may charge households on default tariffs. It quotes the cap as the annual bill for a household with typical consumption: 2,500 kWh of electricity and 9,500 kWh of gas a year, the [typical domestic consumption values](https://www.ofgem.gov.uk/sites/default/files/2026-05/Review%20of%20typical%20domestic%20consumption%20values%20decision.pdf) it has used since July 2026. Figure 1 shows the typical bill under each cap since January 2025.

```chart
{
  "type": "bar",
  "title": "Figure 1: Typical dual-fuel energy bill by quarter, Direct Debit, Great Britain",
  "subtitle": "Annual rate at 2,500 kWh of electricity and 9,500 kWh of gas under Ofgem's caps (January 2025 to March 2026 calculated by PolicyEngine from Ofgem's rates)",
  "xKey": "quarter",
  "series": [{ "key": "ofgem", "name": "Ofgem cap", "color": "primary" }],
  "data": [
{{fig1_data}}
  ],
  "yLabel": "Typical annual bill (£)",
  "format": { "decimals": 0, "prefix": "£", "separator": true },
  "legend": false
}
```

Until July 2026, Ofgem quoted the cap at its previous typical values of 2,700 kWh of electricity and 11,500 kWh of gas. On 1 July 2026, Ofgem [restated](https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf) the April to June 2026 cap on the current values (£1,477, against £1,641 as announced) and the July to September 2026 cap (£1,663, against £1,862 as announced in May), but not earlier caps. For January 2025 to March 2026, we apply each quarter's average Direct Debit unit rates and standing charges, from Ofgem's announcement of that cap, to the current typical values. Table 1 gives both figures.

**Table 1: Typical dual-fuel bill by quarter, Direct Debit, Great Britain average (£ a year)**

| Quarter | Ofgem's announced cap | Typical values of the announced cap (kWh, electricity and gas) | At 2,500 kWh and 9,500 kWh |
| ------- | --------------------: | -------------------------------------------------------------: | -------------------------: |
{{table1_rows}}

Sources: Ofgem's announcements of each cap, from [January to March 2025](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-january-and-31-march-2025) to [October to December 2026](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-october-and-31-december-2026) and [January to March 2027](https://www.ofgem.gov.uk/news/changes-energy-price-cap-between-1-january-and-31-march-2027), and its [restatement of the April to June and July to September 2026 caps](https://www.ofgem.gov.uk/sites/default/files/2026-06/Summary-of-changes-to-energy-price-cap-1-July-to-30-September-2026-revised-TDCV.pdf). The last column for January 2025 to March 2026 is our calculation from Ofgem's average rates for each quarter. Caps before October 2026 include 5% VAT on electricity; from October 2026 electricity carries no VAT, so, as Ofgem notes, the caps on either side of that change are not directly comparable.

Table 2 and Figure 2 compare Ofgem's January rates with its October rates and with Cornwall Insight's forecast.

**Table 2: Price cap for a typical household paying by Direct Debit, Great Britain average**

|  | October to December 2026 (Ofgem) | January to March 2027 (Ofgem) | Change | January to March 2027 (Cornwall Insight forecast) |
| - | -: | -: | -: | -: |
{{table2_rows}}

Sources: Ofgem, [energy price cap unit rates and standing charges](https://www.ofgem.gov.uk/your-energy-supply/your-energy-bill/energy-price-cap-unit-rates-and-standing-charges); Cornwall Insight, [press release](https://www.cornwall-insight.com/press-releases/energy-bills-set-for-steep-rise-in-january/), 18 November 2026. We compute the typical bills by fuel from Ofgem's rates. Ofgem's rates carry no VAT on electricity and 5% VAT on gas. Cornwall Insight publishes standing charges to the nearest penny a day; the forecast column gives the standing charges its fuel totals imply.

```chart
{
  "type": "bar",
  "title": "Figure 2: Change in energy price cap rates by fuel",
  "subtitle": "Percentage change from Ofgem's October to December 2026 cap to its January to March 2027 cap, Direct Debit, Great Britain average{{fig2_note}}",
  "xKey": "fuel",
  "series": [
    { "key": "unit", "name": "Unit rate", "color": "primary" },
    { "key": "standing", "name": "Standing charge", "color": "quinary" }
  ],
  "data": [
    { "fuel": "Electricity", "unit": {{jan_unit_pct_e:npct1}}, "standing": {{jan_standing_pct_e:npct1}} },
    { "fuel": "Gas", "unit": {{jan_unit_pct_g:npct1}}, "standing": {{jan_standing_pct_g:npct1}} }
  ],
  "yLabel": "Change (%)",
  "format": { "decimals": 1, "suffix": "%", "signed": true }
}
```

At typical consumption, the gas bill changes by {{jan_fuel_change_g:sgbp}} and the electricity bill by {{jan_fuel_change_e:sgbp}} ({{jan_rate_change:sgbp}} in total on Ofgem's rates as published, against Ofgem's {{jan_change:sgbp}}){{gas_share_clause}}.

### Why the cap changed

Ofgem's [letter on the January update](https://www.ofgem.gov.uk/sites/default/files/2026-11/summary-of-changes-to-energy-price-cap-1-January-to-31-March-2027.pdf) attributes the change mainly to wholesale costs. Its wholesale cost allowance rises by 50%, to 56% of the typical bill from 47% in October to December: by 59% for gas and 39% for electricity. Ofgem calls conflict and geopolitical instability in the Middle East "the primary driver" of wholesale prices, which it says historically low European gas storage at the start of winter compounded; it notes that prices reached multiyear highs at the end of October before falling back in early November. It attributes the rise in electricity costs to the role gas plays in setting power prices, together with greater reliance on gas-fired power during periods of low wind. In Ofgem's breakdown, allowances that move with the cap level, including suppliers' earnings allowance, headroom, debt costs and VAT on gas, rise with it.

Ofgem expresses the cap as an annual rate. A household pays the January rates for three months. UK households use on average {{q1_share_e:pct1}} of a year's electricity and {{q1_share_g:pct1}} of a year's gas in January to March.[^1] Applying those shares to the unit-rate part of the bill, and 90 days to the standing charges, the cap changes a typical household's bills over January to March by about {{ex_typ_q1_change:sgbp}}.

Ofgem's cap includes the zero rate of VAT on household electricity, which the [Autumn Budget](https://www.gov.uk/government/publications/budget-2026-document/budget-2026-html) extended to July 2027. It leaves out the one-off £100 Household Energy Payment, which the Autumn Budget announced for households in council tax bands A to D in England from January 2027 and which local authorities pay outside the cap, and the Government's plan to remove standing charges from household gas bills, which the Budget asks Ofgem to deliver by the end of 2027 or as soon as possible after, with no start date set. Ofgem sets the cap for April to June 2027 separately, in February 2027.

## Household examples

Table 3 and Figures 3 and 4 apply the rates in Table 2 to four levels of consumption, without the PolicyEngine model: half the typical values (1,250 kWh of electricity and 4,750 kWh of gas), the typical values, double the typical values (5,000 kWh and 19,000 kWh), and a home with no gas using 2,500 kWh of electricity, Ofgem's typical value for a single-rate electricity meter.

```chart
{
  "type": "bar",
  "title": "Figure 3: Annual energy bill by household type, Direct Debit",
  "subtitle": "Annual rate, at Ofgem's October to December 2026 rates and its January to March 2027 rates",
  "xKey": "household",
  "series": [
    { "key": "oct", "name": "October to December 2026", "color": "quinary" },
    { "key": "jan", "name": "January to March 2027", "color": "primary" }
  ],
  "data": [
{{fig3_data}}
  ],
  "yLabel": "Annual bill (£)",
  "format": { "decimals": 0, "prefix": "£", "separator": true }
}
```

```chart
{
  "type": "bar",
  "title": "Figure 4: Annual energy bill by fuel and household type under the January to March 2027 cap, Direct Debit",
  "subtitle": "Annual rate at Ofgem's January to March 2027 rates; the label gives the total",
  "xKey": "household",
  "series": [
    { "key": "electricity", "name": "Electricity", "color": "primary" },
    { "key": "gas", "name": "Gas", "color": "quinary" }
  ],
  "data": [
{{fig4_data}}
  ],
  "yLabel": "Annual bill (£)",
  "format": { "decimals": 0, "prefix": "£", "separator": true },
  "stacked": true
}
```

**Table 3: Annual bill by household type, October to December 2026 against January to March 2027, Direct Debit**

| Household | Electricity | Gas | Total | Standing charges | Unit rates | Change, annual rate | Change over January to March |
| --------- | ----------: | --: | ----: | ---------------: | ---------: | ------------------: | ---------------------------: |
{{table3_rows}}

Cells with two figures give the October bill, then the January bill, at annual rates. The standing charge and unit-rate columns split the total bill. Figures may not sum because of rounding. The last column applies the change in unit rates to the shares of a year's electricity ({{q1_share_e:pct1}}) and gas ({{q1_share_g:pct1}}) used in January to March and the change in standing charges to 90 days, as for the typical household above. Ofgem publishes its rates to two decimal places, so the typical bill here can differ from Ofgem's headline by £1.

Standing charges change by {{jan_standing_pct_e:spct1}} (electricity) and {{jan_standing_pct_g:spct1}} (gas), and unit rates by {{jan_unit_pct_e:spct1}} and {{jan_unit_pct_g:spct1}}, so the bill changes by {{ex_low_change_pct:spct1}} at low use, {{ex_typ_change_pct:spct1}} at typical use and {{ex_high_change_pct:spct1}} at high use. Standing charges make up {{ex_low_standing_share_jan:pct1}} of the low-use bill in January and {{ex_high_standing_share_jan:pct1}} of the high-use bill. A home without gas using 2,500 kWh faces a change of {{ex_eo_change_pct:spct1}}, against {{ex_typ_change_pct:spct1}} at typical use of both fuels, because the typical electricity bill changes by {{jan_bill_pct_e:spct1}} and the typical gas bill by {{jan_bill_pct_g:spct1}} (Table 2). In our data, households that do not use gas spend an average of {{elec_only_mean_before:gbp}} a year on electricity at October prices, against {{ex_eo_oct_total:gbp}} at 2,500 kWh.

## Bills across the income distribution

We apply Ofgem's cap to the electricity and gas spending of every household in Great Britain in PolicyEngine UK's data, [Microcosm UK](https://www.policyengine.org/uk/model/data). We first restate each household's spending at October to December 2026 prices, using PolicyEngine UK's energy price indices. We then change each household's electricity spending by {{jan_bill_pct_e:spct1}} and its gas spending by {{jan_bill_pct_g:spct1}}, the changes in the typical bill for each fuel in Table 2. All figures are annual rates and assume that households do not change how much energy they use. At October prices, households that use both fuels spend an average of {{dual_mean_before:gbp}} a year in our data, and the median such household spends {{dual_median_before:gbp}}, against Ofgem's typical bill of {{oct_total:gbp}}.

```chart
{
  "type": "bar",
  "title": "Figure 5: Average household energy bill by income decile, Great Britain",
  "subtitle": "Annual rate, at Ofgem's October to December 2026 rates and its January to March 2027 rates",
  "xKey": "decile",
  "series": [
    { "key": "oct", "name": "October to December 2026", "color": "quinary" },
    { "key": "jan", "name": "January to March 2027", "color": "primary" }
  ],
  "data": [
{{fig5_data}}
  ],
  "yLabel": "Average annual bill (£)",
  "format": { "decimals": 0, "prefix": "£", "separator": true },
  "valueLabels": false
}
```

Households in the top decile spend more on energy than those in the bottom (Figure 5). Their bills change by an average of {{d10_change:sgbp}} a year, against {{d1_change:sgbp}} in the bottom decile (Figure 7).{{decile_sign_note}} As a share of net income (Figure 6 and Table 4), spending goes from {{d1_share_before:pct1}} to {{d1_share_after:pct1}} in the bottom decile and from {{d10_share_before:pct1}} to {{d10_share_after:pct1}} in the top.

```chart
{
  "type": "bar",
  "title": "Figure 6: Household energy spending as a share of net income by income decile, Great Britain",
  "subtitle": "Total energy spending in each decile over its total net income before housing costs, at annual rates",
  "xKey": "decile",
  "series": [
    { "key": "oct", "name": "October to December 2026", "color": "quinary" },
    { "key": "jan", "name": "January to March 2027", "color": "primary" }
  ],
  "data": [
{{fig6_data}}
  ],
  "yLabel": "Share of net income (%)",
  "format": { "decimals": 1, "suffix": "%" },
  "valueLabels": false
}
```

```chart
{
  "type": "bar",
  "title": "Figure 7: Change in the average household energy bill by income decile, Great Britain",
  "subtitle": "Annual rate, from Ofgem's October to December 2026 rates to its January to March 2027 rates; {{mean_change:sgbp}} across all households",
  "xKey": "decile",
  "series": [{ "key": "change", "name": "Change in average bill", "color": "primary" }],
  "data": [
{{fig7_data}}
  ],
  "yLabel": "Change in average annual bill (£)",
  "format": { "decimals": 0, "prefix": "£", "signed": true },
  "legend": false
}
```

**Table 4: Household energy bills by income decile, Great Britain (annual rates)**

| Income decile | Average net income | Bill, October rates | Bill, January rates | Change | Share of income, October | Share of income, January |
| ------------- | -----------------: | ------------------: | ------------------: | -----: | -----------------------: | -----------------------: |
{{table4_rows}}

We calculate changes from unrounded bills. Net income is household net income before housing costs, as in the Department for Work and Pensions' Households Below Average Income statistics. We rank households into deciles by that income, adjusted for household size, so that each decile holds a tenth of people in the UK.

In our data, {{n_elec_only:m1}} households in Great Britain have no gas spending. Their bills change by an average of {{elec_only_mean_change:sgbp}} a year, against {{dual_mean_change:sgbp}} for the {{n_dual:m1}} households that use both fuels.

We estimate that at October rates, {{over10_before:m1}} households spend more than 10% of their net income before housing costs on energy, counting the {{zero_income:m1}} with zero income (the Households Below Average Income statistics reset negative incomes to zero). At the January rates, held for a full year, {{over10_after:m1}} would. This is not an official fuel poverty measure. It also differs from the fuel-stress measure in the Autumn Budget, which compares energy spending with income after housing costs; our [analysis of the Budget's energy bill measures](https://policyengine.org/uk/research/budget-2026-energy-bills) uses that measure.

The bills in these figures leave out the support that households receive outside the cap, such as the £100 Household Energy Payment in England, the Warm Home Discount and the Winter Fuel Payment. Net income counts those payments as income, as the Households Below Average Income statistics do for the Warm Home Discount and the Winter Fuel Payment and did for the 2022 energy support.

## Support set against the change

Two Autumn Budget measures bear on bills this winter. The Autumn Budget announced the £100 Household Energy Payment, a one-off payment from January 2027 to households in council tax bands A to D in England, which local authorities pay outside the cap. The zero rate of VAT on household electricity has applied since 1 October 2026, is in both the October and the January caps, and the [Budget](https://www.gov.uk/government/publications/budget-2026-document/budget-2026-html) extended it to July 2027; the Department for Energy Security and Net Zero [says](https://www.gov.uk/government/news/what-the-autumn-budget-2026-means-for-your-energy-bills) it saves households an average of £45 a year. In our data, 5% VAT would add {{vat_cut_oct:gbp}} a year to the average household's electricity bill at October rates and {{vat_cut_jan:gbp}} at January rates. Because both caps carry no VAT on electricity, the zero rate lowers the October-to-January change itself by {{vat_on_change:gbp}} a year for the average household ({{vat_on_change_typ:gbp}} at typical use); the figures in this post already include it.

The payment is made once, while the changes above are annual rates. Table 5 and Figure 8 set the payment against the change over January to March, the three months the January cap covers, for households in England, where the payment applies; Table 5 also gives the annual-rate change. We approximate that change by multiplying each household's annual change for each fuel by the share of a year's use in January to March ({{q1_share_e:pct1}} for electricity and {{q1_share_g:pct1}} for gas); this applies the same share to standing charges, which accrue evenly through the year. For the average household in England, bills change by {{mean_change_q1:sgbp}} over January to March and the payment averages {{hep_mean:gbp}}, {{hep_offset_q1:pct0}} of that change ({{hep_offset_annual:pct0}} of the {{mean_change_eng:sgbp}} annual-rate change). For a typical household in England that receives it, £100 is {{hep_typ_share_q1:pct0}} of the {{ex_typ_q1_change:sgbp}} change over January to March, against {{hep_typ_share_annual:pct0}} of the {{jan_change:sgbp}} annual-rate change.

**Table 5: Change in the average household energy bill by income decile, and the Household Energy Payment, England (£)**

| Income decile | Change in bill, annual rate | Change over January to March | Household Energy Payment | Change over January to March less the payment |
| ------------- | --------------------------: | ---------------------------: | -----------------------: | --------------------------------------------: |
{{support_rows}}

The table covers households in England only. The payment column averages the £100 over all households in England in each decile, including those in bands E and above, which do not receive it. The Welsh and Scottish payments described below are not modelled.

```chart
{
  "type": "bar",
  "title": "Figure 8: Change in the average household energy bill over January to March 2027 by income decile, before and after the Household Energy Payment, England",
  "subtitle": "From Ofgem's October to December 2026 rates to its January to March 2027 rates, over the three months; less the one-off £100 Household Energy Payment (England, council tax bands A to D), averaged over all households in England",
  "xKey": "decile",
  "series": [
    { "key": "q1", "name": "Change over January to March", "color": "quinary" },
    { "key": "q1_net_hep", "name": "Less the payment", "color": "primary" }
  ],
  "data": [
{{support_fig_data}}
  ],
  "yLabel": "Change in average bill over January to March (£)",
  "format": { "decimals": 0, "prefix": "£", "signed": true },
  "valueLabels": false
}
```

## Who the Household Energy Payment reaches

We estimate that {{hep_recipients:m1}} households receive the payment, {{hep_share_england:pct0}} of households in England, at a cost of £{{hep_cost:bn2}} billion. The Budget gives £2.6 billion, "supporting up to 20 million households"; that sum also funds £100 million for local authorities and the share that Scotland, Wales and Northern Ireland receive through the Barnett formula. Our [analysis of the Budget's energy bill measures](https://policyengine.org/uk/research/budget-2026-energy-bills) puts the payments in England at £2.10 billion, of which our estimate is 94%.

The Welsh Government [has said](https://www.gov.wales/written-statement-welsh-government-response-uk-autumn-budget-2026) it will make a £100 cost-of-living payment to households in council tax bands A to D, and the Scottish Government [has said](https://www.gov.scot/news/uk-budget-delivers-real-cut-to-scotlands-funding/) that households in Scotland will receive a one-time £100 payment, without saying which households. We model neither, so the figures below cover England only.

Figure 9 shows the share of households in each income decile that receive the payment. In the lowest income decile, {{hep_d1_share_england:pct0}} of households in England receive it and {{hep_d1_missed_england:pct0}} ({{hep_d1_missed_england_m:m1}}) do not, because they live in a home in council tax band E or above. In the highest decile, {{hep_d10_share_england:pct0}} of households in England receive it.

```chart
{
  "type": "bar",
  "title": "Figure 9: Share of households receiving the Household Energy Payment by income decile",
  "subtitle": "Households in council tax bands A to D in England receive £100; share of households in England in each income decile",
  "xKey": "decile",
  "series": [
    { "key": "england", "name": "England", "color": "primary" }
  ],
  "data": [
{{hep_fig_data}}
  ],
  "yLabel": "Households receiving the payment (%)",
  "format": { "decimals": 0, "suffix": "%" },
  "valueLabels": false
}
```

The model pays every household in a home in bands A to D in England. The Government [says](https://www.gov.uk/government/news/what-the-autumn-budget-2026-means-for-your-energy-bills) that households where the householder is not responsible for paying council tax are not eligible; our data cannot identify them, so we overstate the number of recipients by an amount we cannot estimate. We also leave out the £100 million the Budget gives local authorities for further targeted support.

## Ofgem's cap against the forecast

Cornwall Insight forecast a typical bill of {{fc_total:gbp}}; Ofgem's cap is {{jan_total:gbp}}. Table 6 and Figure 10 run both through the same model and data, so the differences come from the rates alone. Ofgem's unit rates are above the forecast and its standing charges below, so the two give much the same typical bill: {{jan_typical_exact:gbp2}} on Ofgem's rates against {{fc_typical_exact:gbp2}} on Cornwall Insight's figures for each fuel, both of which round to £2,166. That small gap is why our estimates differ by about £1. At other levels of use the mix matters more: {{mix_sentence}} Our method, which scales each household's spending by the change in the typical bill, does not capture this.

**Table 6: Cornwall Insight's forecast and Ofgem's cap for January to March 2027, Great Britain (annual rates)**

|  | Cornwall Insight forecast (18 November) | Ofgem cap ({{ofgem_date}}) | Difference |
| - | -: | -: | -: |
{{forecast_rows}}

The forecast's standing charges are those its fuel totals imply, as in Table 2.

```chart
{
  "type": "bar",
  "title": "Figure 10: Change in the average household energy bill by income decile, forecast and actual cap, Great Britain",
  "subtitle": "Annual rate, from Ofgem's October to December 2026 rates to Cornwall Insight's January to March 2027 forecast and to Ofgem's January to March 2027 cap",
  "xKey": "decile",
  "series": [
    { "key": "forecast", "name": "Cornwall Insight forecast", "color": "quinary" },
    { "key": "ofgem", "name": "Ofgem cap", "color": "primary" }
  ],
  "data": [
{{forecast_fig_data}}
  ],
  "yLabel": "Change in average annual bill (£)",
  "format": { "decimals": 0, "prefix": "£", "signed": true },
  "valueLabels": false
}
```

Our earlier post estimated an average change of {{prev_mean_change:sgbp}} on Cornwall Insight's forecast with `policyengine` {{prev_pe_version}} (PolicyEngine UK {{prev_pe_uk_version}}, Microcosm build {{prev_build_short}}). This post uses `policyengine` {{pe_version}} (PolicyEngine UK {{pe_uk_version}}, Microcosm build {{build_short}}), a newer model and dataset; with them, the same forecast gives {{fc_mean_change:sgbp}}, and the October figures move too: the bottom decile's energy spending is {{d1_share_before:pct1}} of its net income, against {{prev_d1_share_before:pct1}} in the earlier post, and {{over10_before:m1}} households spend more than 10% of their net income on energy, against {{prev_over10_before:m1}}.

## Methodology

We use [PolicyEngine UK {{pe_uk_version}}](https://github.com/PolicyEngine/policyengine-uk/tree/{{pe_uk_version}}) with Microcosm UK build {{build_short}}, the pair that the `policyengine` Python package certifies in version {{pe_version}}. PolicyEngine UK's energy price indices, which follow the Office for Budget Responsibility's October 2026 forecast, restate each household's 2026-27 spending at October to December 2026 prices. Microcosm prices electricity with 5% VAT, which we remove to match Ofgem's rates. We leave out Northern Ireland, which the Ofgem cap does not cover.

The method has five limitations:

- **Tariffs.** We apply the cap change to every household. The cap covers default tariffs; households on fixed tariffs see no change in January.
- **Payment method.** We apply the Direct Debit change to every household. Ofgem sets a different cap for standard credit and prepayment, and our data do not separate Direct Debit from standard credit.
- **Standing charges.** We scale each household's spending on a fuel by one factor, the change in the typical bill, so households that use less or more than the typical amount get the typical household's percentage change. For a household using half the typical amount, the cap gives {{half_pct_e:spct1}} against {{typ_pct_e:spct1}} for electricity and {{half_pct_g:spct1}} against {{typ_pct_g:spct1}} for gas.
- **Annual rates.** We hold the January rates for a full year, as Ofgem's typical bill does. Ofgem sets the cap for April to June 2027 separately, in February 2027.
- **Fixed use.** We hold each household's energy use fixed as prices change.

The code, the cap inputs and the aggregated results behind this post are in the [post folder](https://github.com/PolicyEngine/uk-energy-price-cap-jan-2027/tree/main/post) of the uk-energy-price-cap-jan-2027 repository.

[^1]: DESNZ, Energy Trends, [electricity](https://www.gov.uk/government/statistics/electricity-section-5-energy-trends) (ET 5.2) and [gas](https://www.gov.uk/government/statistics/gas-section-4-energy-trends) (ET 4.1): the mean shares of a year's UK domestic consumption used in January to March, 2015 to 2025, which PolicyEngine UK holds as parameters ({{q1_share_e:pct2}} for electricity and {{q1_share_g:pct2}} for gas).
