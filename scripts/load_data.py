"""Load every CSV in data/raw/ into SQLite (one table per file).

Usage: python scripts/load_data.py [--db data/app.db] [--raw data/raw]
"""
import argparse
import re
import sqlite3
from pathlib import Path

import pandas as pd


def table_name(path: Path) -> str:
    return re.sub(r"\W+", "_", path.stem).strip("_").lower()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--db", default="data/app.db")
    p.add_argument("--raw", default="data/raw")
    args = p.parse_args()

    csvs = sorted(Path(args.raw).glob("*.csv"))
    if not csvs:
        raise SystemExit(f"No CSVs found in {args.raw}/ - download a Kaggle dataset first.")
    with sqlite3.connect(args.db) as conn:
        for csv in csvs:
            name = table_name(csv)
            rows = 0
            for i, chunk in enumerate(pd.read_csv(csv, chunksize=50_000, low_memory=False)):
                chunk.columns = [re.sub(r"\W+", "_", c).strip("_").lower() for c in chunk.columns]
                chunk.to_sql(name, conn, if_exists="replace" if i == 0 else "append", index=False)
                rows += len(chunk)
            print(f"{csv.name} -> {name} ({rows:,} rows)")


if __name__ == "__main__":
    main()
