"""Runs every sql/*.sql file against the cleaned data and saves each result
to output/. DuckDB runs in memory, the tables get rebuilt from the CSVs
each time (takes about a second)."""

from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "data" / "processed"
REF = ROOT / "data" / "reference"
SQL_DIR = ROOT / "sql"
OUT = ROOT / "output"


def load_tables(con):
    con.execute(f"""
        CREATE OR REPLACE TABLE imports AS
        SELECT * FROM read_csv_auto('{PROC / "furniture_imports.csv"}',
                                    types={{'hs6': 'VARCHAR', 'country_code': 'VARCHAR'}})
    """)
    con.execute(f"""
        CREATE OR REPLACE TABLE policy_phases AS
        SELECT phase_id, phase,
               CAST(start_month AS DATE) AS start_month,
               CAST(end_month AS DATE)   AS end_month,
               what_changed
        FROM read_csv_auto('{REF / "policy_phases.csv"}')
    """)

    bls = PROC / "bls_import_prices.csv"
    if bls.exists():
        con.execute(f"CREATE OR REPLACE TABLE bls_prices AS SELECT * FROM read_csv_auto('{bls}')")

    n = con.execute("SELECT COUNT(*) FROM imports").fetchone()[0]
    print(f"loaded {n:,} import rows into DuckDB\n")


def main():
    OUT.mkdir(exist_ok=True)
    con = duckdb.connect()
    load_tables(con)

    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        result = con.execute(sql_file.read_text()).df()
        out_file = OUT / f"{sql_file.stem}.csv"
        result.to_csv(out_file, index=False)
        print(f"{sql_file.name:<32} {len(result):>5} rows -> {out_file.relative_to(ROOT)}")

    con.close()


if __name__ == "__main__":
    main()
