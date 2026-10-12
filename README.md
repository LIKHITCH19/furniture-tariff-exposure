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

Work in progress. So far this has the two download scripts:

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

## Data sources

- US Census Bureau, [International Trade API](https://www.census.gov/data/developers/data-sets/international-trade.html),
  imports by HS code and country (`timeseries/intltrade/imports/hs`), Jan 2023 - Aug 2026.
- US Bureau of Labor Statistics, [Import/Export Price Indexes](https://www.bls.gov/mxp/),
  series EIUIR41000 and EIUIR.
- Tariff policy sources are listed in [docs/tariff_timeline.md](docs/tariff_timeline.md).
