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

I don't have a real company's data, so the importer is made up. All the
market numbers are real.

Work in progress. So far: the download scripts, the cleaned data and checks, and the SQL analysis.

Download scripts:

- `src/fetch_census.py` pulls monthly imports by country for 14 furniture
  product lines (HS chapter 94) from the Census trade API, including the duty
  Census calculates on them.
- `src/fetch_bls.py` pulls the BLS import price index for furniture.

The tariff rules changed a lot over this period, so I wrote down what changed
when in [docs/tariff_timeline.md](docs/tariff_timeline.md).

## Getting the data

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # then paste your Census API key into .env
python src/fetch_census.py
python src/fetch_bls.py
```

The Census API needs a key now (free, takes a minute):
https://api.census.gov/data/key_signup.html. The BLS script works without one.

Then `python src/clean.py` builds the cleaned table and `python src/check_data.py`
runs the checks.

## Questions

Each query in `sql/` answers one question. `python src/run_analysis.py` runs
them all with DuckDB and saves the results to `output/`.

| Query | Question |
|---|---|
| `01_monthly_duty_burden` | How has the effective duty rate moved month to month, wood vs non-wood? |
| `02_supplier_share_by_year` | Which countries supply US furniture, and how is that changing? |
| `03_duty_rate_by_country` | What rate does each big supplier actually pay, in each policy phase? |
| `04_sourcing_shift` | Who gained and lost share since 2024 (same months each year)? |
| `05_exposure_by_product` | Which product lines picked up the most extra duty? |
| `06_rate_matrix` | Current rate for each supplier and product line |
| `07_price_vs_duty` | Did suppliers cut prices, or did importers pay the tariff? |

Write-up and charts are next.

## The data

`data/processed/furniture_imports.csv` has one row per month, supplier
country and product line, Jan 2023 to Aug 2026: 41,189 rows across 202
countries and 12 product lines (office chairs and sofa beds, 4 of the 14
codes in the fetch script, aren't in this pull yet). Country groupings like the world total and
"Asia" are split out into `census_totals.csv`, which is only used for the
checks below. Columns are described in [docs/data_dictionary.md](docs/data_dictionary.md).

The cleaned files are committed, so you don't need an API key to work with them.

### Checks

`src/check_data.py` exits with an error if any of these fail:

- Country rows add back up to the Census world total, for both import value
  and duty, in every month and product line (528 cells each, worst gap 0.0000%).
- No gaps in the 44-month series, no duplicate month/country/product rows, no
  negative values.
- Duty rates fall in a sensible range (10 of 30,012 rows above 100%, all
  shipments under $210K).
- Annual totals are national scale ($30-33B a year for these 12 lines).

## Data sources

- US Census Bureau, [International Trade API](https://www.census.gov/data/developers/data-sets/international-trade.html),
  imports by HS code and country (`timeseries/intltrade/imports/hs`), Jan 2023 - Aug 2026.
- US Bureau of Labor Statistics, [Import/Export Price Indexes](https://www.bls.gov/mxp/),
  series EIUIR41000 and EIUIR.
- Tariff policy sources are listed in [docs/tariff_timeline.md](docs/tariff_timeline.md).
