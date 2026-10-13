"""Raw Census pull -> data/processed/furniture_imports.csv

Country groupings (world total, Asia, EU...) go to census_totals.csv
instead. They're only used by check_data.py.
"""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "furniture_imports_raw.csv"
PROC = ROOT / "data" / "processed"

NUMERIC_COLS = ["GEN_VAL_MO", "CON_VAL_MO", "DUT_VAL_MO", "CAL_DUT_MO"]

RENAME = {
    "CTY_CODE": "country_code",
    "CTY_NAME": "country",
    "I_COMMODITY": "hs6",
    "I_COMMODITY_SDESC": "hs_desc",
    "GEN_VAL_MO": "general_imports_usd",
    "CON_VAL_MO": "consumption_imports_usd",
    "DUT_VAL_MO": "dutiable_value_usd",
    "CAL_DUT_MO": "calculated_duty_usd",
}


def find_month_cols(df):
    """Census returns the period as YEAR + MONTH, or sometimes a single 'time'."""
    if "time" in df.columns:
        return "time", None
    if "YEAR" in df.columns and "MONTH" in df.columns:
        return "YEAR", "MONTH"
    sys.exit(f"Cannot find the period columns. Got: {list(df.columns)}")


def build_month(df):
    year_col, month_col = find_month_cols(df)
    if month_col is None:
        df["month"] = pd.to_datetime(df[year_col], format="%Y-%m")
    else:
        year = df[year_col].astype(str).str.strip()
        month = df[month_col].astype(str).str.strip().str.zfill(2)
        df["month"] = pd.to_datetime(year + "-" + month, format="%Y-%m")
    return df


def split_aggregates(df):
    """SUMMARY_LVL is DET for a single country and CGP for groupings like
    Asia or USMCA. The world total has country code "-"."""
    code = df["country_code"].astype(str).str.strip()
    name = df["country"].astype(str).str.upper()

    if "SUMMARY_LVL" in df.columns:
        agg_mask = df["SUMMARY_LVL"].astype(str).str.strip().ne("DET")
    else:
        # older pulls without the flag: fall back on the code and name
        agg_mask = name.str.contains("TOTAL", na=False) | ~code.str.fullmatch(r"\d{4}", na=False)

    agg_mask = agg_mask | code.eq("-")
    return df.loc[~agg_mask].copy(), df.loc[agg_mask].copy()


def main():
    if not RAW_FILE.exists():
        sys.exit(f"{RAW_FILE} not found. Run src/fetch_census.py first.")

    df = pd.read_csv(RAW_FILE, dtype=str)
    start_rows = len(df)

    df = build_month(df)

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df = df.rename(columns=RENAME)
    df["is_wood"] = df["is_wood"].astype(str).str.lower().isin(["true", "1"])
    df["country"] = df["country"].str.strip().str.title()
    df["year"] = df["month"].dt.year

    countries, aggregates = split_aggregates(df)

    # effective rate = calculated duty / value entered for consumption.
    # lots of cells have zero value, leave those blank
    value = countries["consumption_imports_usd"]
    countries["effective_duty_rate"] = countries["calculated_duty_usd"] / value.where(value > 0)

    keep = [
        "month", "year", "country", "country_code",
        "hs6", "hs_label", "hs_desc", "is_wood",
        "general_imports_usd", "consumption_imports_usd",
        "dutiable_value_usd", "calculated_duty_usd", "effective_duty_rate",
    ]
    countries = countries[[c for c in keep if c in countries.columns]]
    countries = countries.sort_values(["month", "hs6", "country"])

    PROC.mkdir(parents=True, exist_ok=True)
    countries.to_csv(PROC / "furniture_imports.csv", index=False)
    aggregates.to_csv(PROC / "census_totals.csv", index=False)

    print(f"raw rows in            : {start_rows:,}")
    print(f"country rows kept      : {len(countries):,}")
    print(f"aggregate rows set aside: {len(aggregates):,}")
    print(f"months covered         : {countries['month'].min():%Y-%m} to {countries['month'].max():%Y-%m}")
    print(f"countries              : {countries['country'].nunique()}")
    print(f"HS6 lines              : {countries['hs6'].nunique()}")
    print(f"\nwrote {(PROC / 'furniture_imports.csv').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
