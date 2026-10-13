"""Checks on the cleaned data. Exits with an error if a hard check fails,
which makes run_all.py stop before the analysis."""

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"

# A tenth of a percent of the total is well inside Census rounding and
# suppression noise; anything bigger means the cleaning lost rows.
SUM_TOLERANCE = 0.001

failures = []
warnings = []


def report(name, ok, detail, hard=True):
    label = "PASS" if ok else ("FAIL" if hard else "WARN")
    print(f"[{label}] {name}")
    if detail:
        print(f"        {detail}")
    if not ok:
        (failures if hard else warnings).append(name)


def check_country_sum(countries, totals):
    """Country rows should add back up to the world total Census publishes."""
    if totals.empty:
        report("country rows add up to Census total", False,
               "no aggregate rows found to compare against - cannot verify",
               hard=False)
        return

    tot = totals.copy()
    # The world total carries a "-" code. If it is ever missing, the broadest
    # aggregate for each month/HS line is the next best thing.
    world_rows = tot[tot["country_code"].astype(str).str.strip() == "-"]
    if world_rows.empty:
        world_rows = tot
    # both value and duty have to reconcile
    for col, what in [("general_imports_usd", "import value"), ("calculated_duty_usd", "duty")]:
        world = (world_rows.groupby(["month", "hs6"], as_index=False)[col].max()
                           .rename(columns={col: "census_total"}))
        ours = (countries.groupby(["month", "hs6"], as_index=False)[col]
                         .sum().rename(columns={col: "our_sum"}))

        merged = world.merge(ours, on=["month", "hs6"], how="inner")
        if merged.empty:
            report(f"country rows add up to Census total ({what})", False,
                   "no overlapping month/HS keys to compare", hard=False)
            continue

        merged = merged[merged["census_total"] > 0]
        merged["gap_pct"] = (merged["our_sum"] - merged["census_total"]).abs() / merged["census_total"]
        bad = merged[merged["gap_pct"] > SUM_TOLERANCE]

        report(
            f"country rows add up to Census total ({what})",
            bad.empty,
            f"{len(merged)} month/HS cells compared, worst gap {merged['gap_pct'].max():.4%}"
            + ("" if bad.empty else f", {len(bad)} cells over tolerance"),
        )


def check_no_missing_months(df):
    """Every HS line should cover every month in the pull, start to finish."""
    gaps = []
    expected = pd.date_range(df["month"].min(), df["month"].max(), freq="MS")
    for hs6, grp in df.groupby("hs6"):
        months = pd.to_datetime(grp["month"].unique())
        missing = expected.difference(months)
        if len(missing):
            gaps.append(f"{hs6}: {', '.join(m.strftime('%Y-%m') for m in missing)}")

    report("no gaps in the monthly series", not gaps,
           "; ".join(gaps) if gaps else f"{df['month'].nunique()} consecutive months")


def check_unique_keys(df):
    key = ["month", "country_code", "hs6"]
    dupes = df.duplicated(subset=key).sum()
    report("one row per month / country / HS6", dupes == 0,
           f"{dupes} duplicate keys" if dupes else f"{len(df):,} unique rows")


def check_no_negatives(df):
    cols = ["general_imports_usd", "consumption_imports_usd", "calculated_duty_usd"]
    neg = {c: int((df[c] < 0).sum()) for c in cols}
    bad = {c: n for c, n in neg.items() if n}
    report("no negative values", not bad, str(bad) if bad else "all three value columns clean")


def check_duty_rate_range(df):
    """Most rates should be 0-60%. A few over 100% show up on tiny shipments,
    but lots of them would point to a problem in the value or duty columns."""
    rated = df[df["consumption_imports_usd"] > 0].dropna(subset=["effective_duty_rate"])
    if rated.empty:
        report("duty rates in a sensible range", False, "no rows with a duty rate", hard=False)
        return

    over = rated[rated["effective_duty_rate"] > 1.0]
    share = len(over) / len(rated)

    report("duty rates in a sensible range", share < 0.01,
           f"median {rated['effective_duty_rate'].median():.2%}, "
           f"p99 {rated['effective_duty_rate'].quantile(0.99):.2%}, "
           f"{len(over)} of {len(rated):,} rows over 100% ({share:.3%})")


def check_duty_only_where_goods(df):
    """Duty with no goods behind it in the same cell is a red flag."""
    odd = df[(df["calculated_duty_usd"] > 0) & (df["consumption_imports_usd"] == 0)]
    report("no duty charged on zero-value entries", odd.empty,
           f"{len(odd)} rows with duty but no consumption value"
           if len(odd) else "none found",
           hard=False)


def check_coverage(df):
    """Sanity floor: this should look like national-scale furniture trade."""
    annual = df.groupby("year")["general_imports_usd"].sum()
    full_years = annual[annual.index < df["year"].max()]
    ok = (full_years > 5e9).all() if len(full_years) else False
    detail = ", ".join(f"{y}: ${v/1e9:.1f}B" for y, v in annual.items())
    report("annual totals are national scale", ok, detail)


def main():
    cfile = PROC / "furniture_imports.csv"
    if not cfile.exists():
        sys.exit(f"{cfile} not found. Run src/clean.py first.")

    ids = {"hs6": str, "country_code": str}
    countries = pd.read_csv(cfile, parse_dates=["month"], dtype=ids)
    tfile = PROC / "census_totals.csv"
    totals = (pd.read_csv(tfile, parse_dates=["month"], dtype=ids)
              if tfile.exists() else pd.DataFrame())

    print(f"checking {len(countries):,} rows, "
          f"{countries['month'].min():%Y-%m} to {countries['month'].max():%Y-%m}\n")

    check_country_sum(countries, totals)
    check_no_missing_months(countries)
    check_unique_keys(countries)
    check_no_negatives(countries)
    check_duty_rate_range(countries)
    check_duty_only_where_goods(countries)
    check_coverage(countries)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed: {', '.join(failures)}")
        sys.exit(1)
    if warnings:
        print(f"all hard checks passed, {len(warnings)} warning(s): {', '.join(warnings)}")
    else:
        print("all checks passed")


if __name__ == "__main__":
    main()
