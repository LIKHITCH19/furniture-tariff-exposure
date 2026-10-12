"""Downloads monthly furniture imports (HS 94) by country from the Census
international trade API, including calculated duty.

One request per HS6 code per year. Responses are cached in data/raw/cache,
so a rerun only fetches what's missing.

    python src/fetch_census.py            # fetch what's missing
    python src/fetch_census.py --refresh  # download everything again
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CACHE = RAW / "cache"

BASE_URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"

# CON_VAL_MO is the value duty gets assessed on, so it's the denominator for
# the duty rate. GEN_VAL_MO is the headline import number Census publishes.
FIELDS = [
    "MONTH",              # YEAR comes back on its own because it is a filter
    "CTY_CODE",
    "CTY_NAME",
    "SUMMARY_LVL",        # DET = single country, CGP = country grouping
    "I_COMMODITY",
    "I_COMMODITY_SDESC",
    "GEN_VAL_MO",
    "CON_VAL_MO",
    "DUT_VAL_MO",         # the part of the consumption value that is dutiable
    "CAL_DUT_MO",
]

# (label, is_wood). is_wood just follows the HS description. Section 232
# coverage is decided at the 10-digit level, so it doesn't line up exactly.
# HS 2022 split 9401.30 and 9401.40 into wood/other, the old codes return nothing.
HS_CODES = {
    "940131": ("Swivel seats of wood", True),
    "940139": ("Swivel seats, other (mostly office chairs)", False),
    "940141": ("Seats convertible into beds, of wood", True),
    "940149": ("Seats convertible into beds, other", False),
    "940161": ("Upholstered seats with wooden frames", True),
    "940169": ("Other seats with wooden frames", True),
    "940171": ("Upholstered seats with metal frames", False),
    "940179": ("Other seats with metal frames", False),
    "940310": ("Metal office furniture", False),
    "940320": ("Other metal furniture", False),
    "940330": ("Wooden office furniture", True),
    "940340": ("Wooden kitchen furniture (cabinets, vanities)", True),
    "940350": ("Wooden bedroom furniture", True),
    "940360": ("Other wooden furniture", True),
    "940382": ("Bamboo furniture", False),
    "940389": ("Furniture of other materials", False),
}

# 2023-24 = pre-tariff baseline. 2026 is partial, Census runs ~2 months behind.
YEARS = [2023, 2024, 2025, 2026]


def load_key():
    """Read CENSUS_API_KEY from .env or the environment."""
    key = os.environ.get("CENSUS_API_KEY")
    if key:
        return key.strip()

    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() == "CENSUS_API_KEY":
                return value.strip().strip('"').strip("'")

    sys.exit(
        "No Census API key found.\n"
        "Get one free at https://api.census.gov/data/key_signup.html,\n"
        "then copy .env.example to .env and paste it in."
    )


def fetch(hs_code, year, key, session):
    """One API call: all countries, all months, for a single HS6 code and year."""
    params = {
        "get": ",".join(FIELDS),
        "YEAR": str(year),
        "COMM_LVL": "HS6",
        "I_COMMODITY": hs_code,
        "key": key,
    }
    resp = session.get(BASE_URL, params=params, timeout=60)

    # Census answers an empty result set with 204, which is what we get for
    # months that have not been published yet. Not an error.
    if resp.status_code == 204:
        return None
    if resp.status_code != 200:
        snippet = resp.text[:200].replace("\n", " ")
        raise RuntimeError(f"HTTP {resp.status_code} for {hs_code}/{year}: {snippet}")

    # a bad or not-yet-activated key gets redirected to an HTML page, not an error code
    if "key" in resp.url.split("?")[0] or "html" in resp.headers.get("Content-Type", ""):
        raise RuntimeError("Census did not accept the API key. Check CENSUS_API_KEY in .env "
                           "and make sure you clicked the activation link in the signup email.")

    return resp.json()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="ignore cached responses")
    args = ap.parse_args()

    key = load_key()
    CACHE.mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    frames = []
    calls = 0
    failed = []

    for hs_code, (label, is_wood) in HS_CODES.items():
        for year in YEARS:
            cache_file = CACHE / f"{hs_code}_{year}.json"

            if cache_file.exists() and not args.refresh:
                payload = json.loads(cache_file.read_text())
            else:
                try:
                    payload = fetch(hs_code, year, key, session)
                except (RuntimeError, requests.RequestException) as err:
                    # not cached, so the next run tries again. the error text
                    # includes the URL, so mask the key
                    print(f"  ! {hs_code} {year}: {str(err).replace(key, '***')}")
                    failed.append(f"{hs_code}/{year}")
                    continue
                calls += 1
                cache_file.write_text(json.dumps(payload))
                time.sleep(0.4)  # be polite to the API

            if not payload or len(payload) < 2:
                print(f"  - {hs_code} {year}: no data published")
                continue

            header, rows = payload[0], payload[1:]
            df = pd.DataFrame(rows, columns=header)
            # Census echoes filter fields back as extra columns, so
            # I_COMMODITY can show up twice. Keep the first copy.
            df = df.loc[:, ~df.columns.duplicated()]
            df["hs_label"] = label
            df["is_wood"] = is_wood
            frames.append(df)
            print(f"  + {hs_code} {year}: {len(df):>5} rows  ({label})")

    if not frames:
        sys.exit("Nothing fetched. Check the API key and your connection.")

    raw = pd.concat(frames, ignore_index=True)
    out = RAW / "furniture_imports_raw.csv"
    raw.to_csv(out, index=False)

    print(f"\n{len(raw):,} rows from {calls} new API calls -> {out.relative_to(ROOT)}")
    if failed:
        print(f"{len(failed)} request(s) failed ({', '.join(failed)}). Run the script again to retry them.")


if __name__ == "__main__":
    main()
