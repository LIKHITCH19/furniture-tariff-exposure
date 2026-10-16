"""Rebuild everything after a download: clean, checks, SQL, charts,
dashboard, Excel model. Stops if the data checks fail.

Downloading is separate (src/fetch_census.py, src/fetch_bls.py).
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw" / "furniture_imports_raw.csv"

STEPS = [
    "clean.py",
    "check_data.py",
    "run_analysis.py",
    "make_charts.py",
    "build_dashboard.py",
    "build_model.py",
]

if not RAW.exists():
    # a fresh clone has the cleaned data but not the raw download
    print("No raw Census download found - using the cleaned data already in data/processed/.")
    STEPS.remove("clean.py")

for step in STEPS:
    print(f"\n=== {step} ===")
    result = subprocess.run([sys.executable, str(ROOT / "src" / step)], cwd=ROOT)
    if result.returncode != 0:
        sys.exit(f"\n{step} failed - stopping here.")

print("\nDone. Open output/dashboard.html and output/landed_cost_model.xlsx.")
