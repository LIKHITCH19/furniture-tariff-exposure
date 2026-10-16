"""Builds output/dashboard.html from src/dashboard_template.html.

The numbers get embedded as JSON and Plotly.js draws the charts in the
browser, so it's a single file you can open straight from disk.
"""

import json
import math
from pathlib import Path

import pandas as pd

from fetch_census import HS_CODES

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
TEMPLATE = ROOT / "src" / "dashboard_template.html"
PAGE = OUT / "dashboard.html"

EN_DASH = "\u2013"

# short names for chart axes - the table keeps the full HS descriptions
SHORT_LINE = {
    "940131": "Wood swivel seats",
    "940139": "Office chairs (non-wood)",
    "940141": "Wood sofa beds",
    "940149": "Other sofa beds",
    "940161": "Upholstered wood seats",
    "940169": "Other wood-frame seats",
    "940171": "Upholstered metal seats",
    "940179": "Other metal-frame seats",
    "940310": "Metal office furniture",
    "940320": "Other metal furniture",
    "940330": "Wood office furniture",
    "940340": "Kitchen cabinets, vanities",
    "940350": "Wood bedroom furniture",
    "940360": "Other wood furniture",
    "940382": "Bamboo furniture",
    "940389": "Other materials",
}

SHORT_PHASE = {
    "IEEPA tariffs": "IEEPA",
    "IEEPA + Section 232 wood": "IEEPA + §232",
    "Section 122": "§122",
    "Section 301 (2026)": "§301",
}


def clean(value):
    """JSON has no NaN - turn missing numbers into null."""
    if isinstance(value, float) and math.isnan(value):
        return None
    return value


def as_list(series):
    return [clean(float(v)) if v is not None else None for v in series]


def month_str(ts):
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def build_data():
    imports = pd.read_csv(ROOT / "data" / "processed" / "furniture_imports.csv",
                          dtype={"hs6": str}, parse_dates=["month"])
    monthly = pd.read_csv(OUT / "01_monthly_duty_burden.csv", parse_dates=["month"])
    shift = pd.read_csv(OUT / "04_sourcing_shift.csv")
    products = pd.read_csv(OUT / "05_exposure_by_product.csv", dtype={"hs6": str})
    prices = pd.read_csv(OUT / "07_price_vs_duty.csv", parse_dates=["month"])
    phases = pd.read_csv(ROOT / "data" / "reference" / "policy_phases.csv",
                         parse_dates=["start_month", "end_month"])

    start, latest = imports["month"].min(), imports["month"].max()
    wide = monthly.pivot(index="month", columns="segment", values="effective_rate")

    # --- policy phases, clipped to the months we actually have
    phase_rows = []
    for _, p in phases.iterrows():
        end = p["end_month"] if pd.notna(p["end_month"]) else latest
        months = imports.loc[imports["month"].between(p["start_month"], end), "month"].nunique()
        x0 = p["start_month"] - pd.Timedelta(days=15)
        x1 = end + pd.Timedelta(days=15)
        when = f"{p['start_month']:%b %Y} to " + (f"{end:%b %Y}" if pd.notna(p["end_month"]) else "now")
        phase_rows.append({
            "name": p["phase"], "short": SHORT_PHASE.get(p["phase"], p["phase"]),
            "when": when, "what": p["what_changed"], "months": int(months),
            "x0": month_str(x0), "x1": month_str(x1), "mid": month_str(x0 + (x1 - x0) / 2),
        })

    # --- headline figures
    y2024 = imports[imports["year"] == 2024]
    rate_2024 = y2024["calculated_duty_usd"].sum() / y2024["consumption_imports_usd"].sum()
    china = shift.set_index("country").loc["China"]
    last_price = prices.dropna(subset=["pre_duty_index"]).iloc[-1]
    period = shift["period_compared"].iloc[0]           # e.g. "Jan-Aug, 2024 vs 2026"
    months_part, years_part = period.split(", ")
    kpis = {
        "rate_now": float(wide["All furniture"].iloc[-1]),
        "rate_2024": float(rate_2024),
        "extra_duty": float(products["extra_duty_usd"].sum()),
        "china_base": float(china["share_base"]),
        "china_now": float(china["share_latest"]),
        "period": months_part.replace("-", EN_DASH) + " " + years_part.split(" vs ")[1],
        "price_change": float(last_price["pre_duty_index"] / 100 - 1),
        "cost_change": float(last_price["with_duty_index"] / 100 - 1),
    }

    # --- monthly rate for the biggest suppliers
    top = imports.groupby("country")["general_imports_usd"].sum().nlargest(10).index
    by_country = (imports[imports["country"].isin(top)]
                  .groupby(["country", "month"])[["calculated_duty_usd", "consumption_imports_usd"]].sum())
    rate_by_country = (by_country["calculated_duty_usd"] / by_country["consumption_imports_usd"]).unstack(0)
    suppliers = {
        "months": [month_str(m) for m in rate_by_country.index],
        "all": as_list(wide["All furniture"].reindex(rate_by_country.index)),
        "rates": {c: as_list(rate_by_country[c]) for c in top},
    }

    # --- sourcing shift
    s = shift[shift["share_change_pts"].abs() >= 0.1].sort_values("share_change_pts", ascending=False)
    shift_data = {
        "period": period.replace("-", EN_DASH),
        "countries": s["country"].tolist(),
        "pts": as_list(s["share_change_pts"]),
        "value_pct": as_list(s["value_change_pct"]),
    }

    # --- product table
    product_rows = [{
        "hs6": r["hs6"], "label": r["hs_label"], "short": SHORT_LINE.get(r["hs6"], r["hs_label"]), "wood": bool(r["is_wood"]),
        "imports": clean(r["ttm_imports_usd"]), "import_change": clean(r["import_change_pct"]),
        "base_rate": clean(r["base_rate"]), "rate": clean(r["ttm_rate"]),
        "extra": clean(r["extra_duty_usd"]),
        "china_base": clean(r["base_china_share"]), "china_now": clean(r["ttm_china_share"]),
    } for _, r in products.iterrows()]

    # --- price vs duty, from 2024 on
    pr = prices[prices["month"] >= "2024-01-01"]
    price_data = {
        "months": [month_str(m) for m in pr["month"]],
        "pre": as_list(pr["pre_duty_index"]),
        "with": as_list(pr["with_duty_index"]),
    }

    # --- say so on the page if any product line in the fetch list has no data
    missing = sorted(set(HS_CODES) - set(imports["hs6"].unique()))
    missing_note = ""
    if missing:
        labels = ", ".join(f"{HS_CODES[c][0].lower()} ({c})" for c in missing)
        missing_note = f"Not yet in this build: {labels}. Rerun src/fetch_census.py to add them."

    ttm_start = latest - pd.DateOffset(months=11)
    meta = {
        "start": month_str(start), "latest": month_str(latest),
        "lines": int(imports["hs6"].nunique()),
        "countries": int(imports.loc[imports["general_imports_usd"] > 0, "country"].nunique()),
        "ttm": f"{ttm_start:%b %Y} to {latest:%b %Y}",
        "missing": missing_note,
    }

    return {
        "meta": meta, "phases": phase_rows, "kpis": kpis,
        "monthly": {"months": [month_str(m) for m in wide.index],
                    "all": as_list(wide["All furniture"]), "wood": as_list(wide["Wood furniture"]),
                    "nonwood": as_list(wide["Non-wood furniture"])},
        "suppliers": suppliers, "shift": shift_data, "products": product_rows, "prices": price_data,
    }


def main():
    data = build_data()
    page = TEMPLATE.read_text().replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    OUT.mkdir(exist_ok=True)
    PAGE.write_text(page)
    print(f"wrote {PAGE.relative_to(ROOT)}  ({len(page) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
