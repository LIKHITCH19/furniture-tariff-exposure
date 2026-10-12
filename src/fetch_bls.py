"""Downloads the BLS import price indexes for furniture (EIUIR41000) and
all imports (EIUIR).

BLS import prices exclude duty, which is why they're useful here: if duty
went up and these prices didn't come down, the importer paid the tariff.
The v1 API doesn't need a key.
"""

import os
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
# small and already tidy, so it goes straight to processed/ (and gets committed)
OUT = ROOT / "data" / "processed" / "bls_import_prices.csv"

SERIES = {
    "EIUIR41000": "Import price index: furniture, household goods (end use)",
    "EIUIR": "Import price index: all imports",
}

START_YEAR, END_YEAR = 2022, 2026


def bls_key():
    key = os.environ.get("BLS_API_KEY")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("BLS_API_KEY="):
                key = line.split("=", 1)[1].strip()
    return key or None


def main():
    key = bls_key()
    version = "v2" if key else "v1"
    url = f"https://api.bls.gov/publicAPI/{version}/timeseries/data/"

    body = {"seriesid": list(SERIES), "startyear": str(START_YEAR), "endyear": str(END_YEAR)}
    if key:
        body["registrationkey"] = key

    resp = requests.post(url, json=body, timeout=60)
    resp.raise_for_status()
    payload = resp.json()

    if payload.get("status") != "REQUEST_SUCCEEDED":
        raise SystemExit(f"BLS said: {payload.get('status')} {payload.get('message')}")

    rows = []
    for series in payload["Results"]["series"]:
        sid = series["seriesID"]
        if not series["data"]:
            print(f"  ! {sid}: no data returned - check the series ID")
            continue
        for obs in series["data"]:
            # M13 is an annual average on some series; skip it
            if not obs["period"].startswith("M") or obs["period"] == "M13":
                continue
            rows.append({
                "series_id": sid,
                "series_name": SERIES.get(sid, sid),
                "month": f"{obs['year']}-{obs['period'][1:]}-01",
                "index_value": pd.to_numeric(obs["value"], errors="coerce"),
                "preliminary": any(f and f.get("code") == "P" for f in obs.get("footnotes", [])),
            })
        print(f"  + {sid}: {sum(r['series_id'] == sid for r in rows)} months")

    df = pd.DataFrame(rows).sort_values(["series_id", "month"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"\nwrote {len(df)} rows -> {OUT.relative_to(ROOT)}")

    for msg in payload.get("message", []):
        print(f"  note from BLS: {msg}")


if __name__ == "__main__":
    main()
