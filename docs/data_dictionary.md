# Data dictionary

## data/processed/furniture_imports.csv

One row per month x supplier country x HS6 product line. Built by
`src/clean.py` from the Census API pull. Country groupings (world total,
Asia, EU, USMCA and so on) are taken out and kept in `census_totals.csv`, which
is only used to check that the country rows add up.

| Column | What it is |
|---|---|
| `month` | First day of the month the goods entered |
| `year` | Calendar year of `month` |
| `country` | Supplier country (Census name, title case) |
| `country_code` | 4-digit Census country code |
| `hs6` | 6-digit Harmonized System code |
| `hs_label` | My short name for the HS6 line |
| `hs_desc` | Census's own description |
| `is_wood` | True if the HS description puts the line under wood furniture or wood-frame seating |
| `general_imports_usd` | General imports, customs value (`GEN_VAL_MO`). The headline import number |
| `consumption_imports_usd` | Imports for consumption, customs value (`CON_VAL_MO`). What duty is assessed on |
| `dutiable_value_usd` | The part of the consumption value that is dutiable (`DUT_VAL_MO`) |
| `calculated_duty_usd` | Duty Census calculates on those entries (`CAL_DUT_MO`) |
| `effective_duty_rate` | `calculated_duty_usd / consumption_imports_usd`. Blank when there is no consumption value |

General imports include goods going into bonded warehouses and free trade
zones; imports for consumption only count goods released into the US economy.
That is why the two value columns differ a little.

## data/processed/bls_import_prices.csv

| Column | What it is |
|---|---|
| `series_id` | BLS series. `EIUIR41000` = furniture, household goods (end use); `EIUIR` = all imports |
| `month` | First day of the month |
| `index_value` | Index level (BLS base: 2000 = 100). Prices exclude duty |
| `preliminary` | True if BLS marks the value preliminary |

## data/reference/policy_phases.csv

Hand-built from `docs/tariff_timeline.md`. One row per policy phase with its
first and last month; the last phase has no end month.

## output/

| File | Question it answers |
|---|---|
| `01_monthly_duty_burden.csv` | Effective duty rate each month, wood vs non-wood |
| `02_supplier_share_by_year.csv` | Each major supplier's share of imports by year |
| `03_duty_rate_by_country.csv` | Effective rate per major supplier in each policy phase |
| `04_sourcing_shift.csv` | Change in share and value, same months two years apart |
| `05_exposure_by_product.csv` | Rate change and extra duty per product line, last 12 months vs 2024 |
| `06_rate_matrix.csv` | Latest 3-month effective rate per supplier x product line |
| `07_price_vs_duty.csv` | BLS pre-duty price index next to a duty-inclusive version |
