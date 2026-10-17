# Furniture tariff exposure

Between February 2025 and August 2026 the tariff rules on imported furniture
changed at least eight times. I wanted to see what that actually did to the
duty US importers paid, using the government's own trade records rather than
headline tariff rates, and then turn it into something a furniture importer
could make a sourcing decision with.

I set it up as if I were the analyst at a mid-size US furniture importer
(about $40M a year of product, a lot of it from China) with three questions
to answer:

1. Which of our product lines are most exposed?
2. Where is the rest of the market moving its sourcing?
3. What would moving our own volume cost or save?

I don't have a real company's data, so the importer in the scenario model is
made up (and labeled that way in the workbook). All the market numbers are
real.

- **Interactive dashboard:** `output/dashboard.html` (download and open in a browser)
- **Scenario model:** `output/landed_cost_model.xlsx`

## Summary

- The effective duty rate on furniture went from 5.3% in 2024 to a peak of
  25.9% in January 2026. It was still 17.5% in August 2026, after the Supreme
  Court threw out the IEEPA tariffs.
- Importers paid $5.2B in duty over the last 12 months, compared with $1.8B
  in all of 2024. About $3.8B of that comes from the higher rates alone.
- Foreign suppliers didn't lower their prices to make up for it. Pre-duty
  import prices have gone up 3.1% since January 2025, so US importers carried
  the cost.
- China's share of US furniture imports fell from 28.2% to 17.0%. Vietnam
  picked up the most share, but Cambodia and Thailand are where volume actually
  grew.
- For the importer in the model, moving its China volume to Vietnam cuts
  landed cost by about 6%, as long as Vietnamese factories don't charge more
  than ~11% above China on upholstered seating and ~20% on bedroom furniture.

## Background

Four separate tariff programs hit furniture in this window, and they stack
differently on different products:

- **IEEPA tariffs** (Feb 2025 - Feb 2026): a China "fentanyl" tariff, then
  reciprocal tariffs on almost everyone. Struck down by the Supreme Court on
  Feb 20, 2026.
- **Section 232** (from Oct 14, 2025): 25% on certain upholstered wooden
  furniture and on kitchen cabinets and vanities, from every country. Still in
  force; a scheduled increase was pushed to 2027.
- **Section 122** (Feb 24 - Jul 24, 2026): a flat 10% stopgap after the ruling.
- **Section 301** (from Jul 24, 2026): 12.5% on China, Vietnam and Thailand,
  10% on Cambodia, Indonesia, Malaysia, Mexico and others.

Dates and sources are in [docs/tariff_timeline.md](docs/tariff_timeline.md).

## 1. How much more duty is furniture paying?

![Effective duty rate by month](images/duty_rate_by_month.png)

The rate is calculated duty divided by the customs value of goods entered, so
it captures exemptions, stacking rules and product mix instead of assuming the
headline rate applies to everything.

Non-wood furniture got hit first because it leans much harder on China. In
2024 China supplied 46% of non-wood furniture imports but only 15% of wood
furniture, and China's tariffs went up first and furthest. Wood furniture
caught up in October 2025 when Section 232 started.
From April 2026 on, both have stayed around 15-18%, roughly three times where
they were in 2024.

## 2. Which product lines are most exposed?

![Extra duty by product line](images/extra_duty_by_product.png)

"Extra duty" is what each line paid in the last 12 months minus what the same
goods would have paid at that line's 2024 rate. Wood lines account for 64% of
the $3.8B.

Upholstered wood-frame seating (HS 940161) is the most exposed line: $955M in
extra duty, its rate up from 4.8% to 22.6%. Section 232 hits it from every
country, so moving production doesn't escape it. Its China share has already
dropped from 26% to 8%.

## 3. Where is sourcing moving?

![Change in share of imports by supplier](images/sourcing_shift.png)

Comparing January-August 2026 with the same months of 2024:

- China lost 11.1 points of share and half its dollar volume ($6.2B to $2.9B).
- Vietnam gained the most share (29.7% to 36.6%), but its dollar volume
  actually fell 3%. The total market shrank 21%, so Vietnam's share went up
  even though it didn't pick up China's lost orders.
- Cambodia (+99%) and Thailand (+69%) are where volume really grew.
- Mexico lost share and a third of its volume. I expected to see some
  nearshoring here and it isn't in the furniture numbers, at least not yet.

![Duty rate by supplier](images/duty_rate_by_country.png)

China still pays about twice the rate of any other big supplier (33.9% since
March 2026, against 17% for Vietnam and Cambodia), because the 2018-19
Section 301 tariffs on Chinese furniture never went away.

## 4. Who paid the tariff?

![Supplier price before and after duty](images/price_vs_duty.png)

The BLS import price index measures what foreign suppliers charge *before*
duty. If suppliers were absorbing the tariffs, it would have dropped as the
duty went up. It went up 3.1%. With duty included, the cost of imported
furniture peaked about 21% above January 2025 and is still about 15% higher.

## 5. What would a sourcing shift do for our importer?

The Excel model takes a made-up $40M-a-year importer and applies the real
duty rates from the last three months of data (Jun-Aug 2026), plus freight and
customs fees, to four sourcing scenarios:

| Scenario | Landed cost | vs today |
|---|---:|---:|
| Today's mix (30-70% China depending on line) | $53.1M | |
| Move China volume to Vietnam | $49.9M | -$3.2M (-6.1%) |
| Spread it across Vietnam, Cambodia, Indonesia | $49.9M | -$3.3M (-6.2%) |
| Nearshore it to Mexico | $48.2M | -$4.9M (-9.3%) |

These assume the new factories charge the same price as China, which they
won't. So the more useful output is the break-even sheet: how much more a
Vietnamese factory can charge before the move stops paying off.

| Product line | Break-even premium, Vietnam vs China |
|---|---:|
| Wooden bedroom furniture | 20.6% |
| Other metal furniture | 20.6% |
| Other wooden furniture | 18.1% |
| Kitchen cabinets and vanities | 11.1% |
| Upholstered wood-frame seating | 10.6% |
| Upholstered metal-frame seating | 7.5% |

## If I were the importer

1. Start with bedroom, other wood and other metal furniture. That's where the
   gap with China is biggest: a new supplier could be about 18-21% more
   expensive and the move would still pay off.
2. Don't expect much from moving upholstered seating or cabinets. Section 232
   applies no matter where they come from, so there's only about 10-11% of
   room. For these, pushing existing suppliers on price is probably worth more
   than switching.
3. Check USMCA qualification before getting excited about Mexico. Mexico comes
   out cheapest in the model because of cheaper freight and low duty on its
   non-upholstered furniture (0% on bedroom, under 5% on metal, most likely
   USMCA goods). Section 232 still hits Mexican seating and cabinets, and if
   the goods don't qualify for USMCA a lot of that advantage disappears.
4. Ask a customs broker about IEEPA refunds. Duty paid under IEEPA between
   February 2025 and February 2026 may be recoverable, and for a company this
   size that could be real money.

## How the numbers were checked

`src/check_data.py` runs before any analysis and stops the pipeline if
something is off:

- Country rows add back up to the Census world total, for both import value
  and duty, in every month and product line (528 cells each, worst gap 0.0000%).
- No gaps in the 44-month series, no duplicate month/country/product rows, no
  negative values.
- Duty rates fall in a sensible range (10 of 30,012 rows above 100%, all
  shipments under $210K).
- Annual totals are national scale ($30-33B a year for these 12 lines).

I also checked a BLS value against FRED's published copy of the same series,
and recalculated every scenario in the Excel model independently in Python;
they match to the dollar.

## Limitations

- HS6 codes are broad, so every rate here is an average across a whole code.
  Section 232 coverage, exclusions and USMCA qualification get decided at the
  10-digit level or per shipment.
- Census "calculated duty" is what got charged at entry. If the IEEPA refunds
  are paid, the real cost for Feb 2025 - Feb 2026 is lower than shown.
- November 2025 has a one-month drop in duty on upholstered seating and
  cabinets from non-China suppliers, then it goes right back in December. I
  couldn't find a policy reason for it, so I left it in and flagged it on the
  chart.
- The BLS series covers "furniture, household goods", which is wider than HS
  chapter 94, but it's the closest monthly series BLS still publishes. It has
  no October 2025 value.
- Office chairs and sofa beds aren't in the numbers yet (their codes were
  split in the 2022 HS revision).
- The importer in the scenario model is made up. Freight rates and the
  sourcing mix are placeholders.

## What I'd do next

- Add office chairs and sofa beds. The new codes are already in
  `src/fetch_census.py`, so it's one rerun.
- Go down to 10-digit HTS codes to separate the lines Section 232 actually
  covers from the rest.
- Rerun once Census publishes September and October 2026, the first full
  months under the new Section 301 rates.
- Rebuild the dashboard in Power BI.

## Run it yourself

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# optional: re-download the raw data (needs a free Census API key in .env,
# see .env.example). The cleaned data is already in data/processed/.
python src/fetch_census.py
python src/fetch_bls.py

# rebuild everything: clean -> checks -> SQL -> charts -> dashboard -> Excel model
python run_all.py
```

## What's in here

```
src/
  fetch_census.py        download monthly imports + duty from the Census API
  fetch_bls.py           download the BLS import price index
  clean.py               tidy table, split out country groupings, duty rate
  check_data.py          data quality checks (stops the pipeline on failure)
  run_analysis.py        runs every query in sql/ with DuckDB
  make_charts.py         PNG charts for this README
  build_dashboard.py     interactive dashboard (template: dashboard_template.html)
  build_model.py         Excel landed-cost scenario model
sql/                     one query per business question
data/
  processed/             cleaned Census data + BLS prices (committed, so the
                         analysis runs without an API key)
  reference/             policy phases, built from docs/tariff_timeline.md
docs/
  tariff_timeline.md     what changed when, with sources
  data_dictionary.md     every column and output file
output/                  query results, dashboard, Excel model
images/                  charts used above
```

## Data sources

- US Census Bureau, [International Trade API](https://www.census.gov/data/developers/data-sets/international-trade.html),
  imports by HS code and country (`timeseries/intltrade/imports/hs`), Jan 2023 - Aug 2026.
- US Bureau of Labor Statistics, [Import/Export Price Indexes](https://www.bls.gov/mxp/),
  series EIUIR41000 and EIUIR.
- Tariff policy sources are listed in [docs/tariff_timeline.md](docs/tariff_timeline.md).

Built with Python (pandas, DuckDB, matplotlib, openpyxl), SQL, Plotly.js and Excel.
