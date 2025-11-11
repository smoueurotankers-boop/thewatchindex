#!/usr/bin/env python3
"""
Aggregate CSV submissions into a single JSON metrics file.

This script reads all `.csv` files in the `submissions` directory,
concatenates their contents, and calculates totals and averages
for sleep hours and rest violations. It also counts reports by ship type
and region. The resulting JSON is written to `data/data.json`.

Expected CSV format (header row):
ship_type,region,sleep_hours,rest_violations,called_during_rest,port_intensity

No personally identifying information should be included in the CSVs.
"""
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

def aggregate_submissions(submissions_path: Path) -> dict:
    totals = {"submissions": 0}
    sums = {"sleep": 0.0, "rest": 0.0}
    by_ship = {}
    by_region = {}
    # Iterate through all CSV files
    for csv_file in submissions_path.glob("*.csv"):
        with csv_file.open(newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic sanity check: skip incomplete rows
                if not row.get('ship_type') or not row.get('region'):
                    continue
                totals["submissions"] += 1
                # Add values
                try:
                    sleep = float(row.get('sleep_hours', 0) or 0)
                except ValueError:
                    sleep = 0.0
                try:
                    rest = float(row.get('rest_violations', 0) or 0)
                except ValueError:
                    rest = 0.0
                sums["sleep"] += sleep
                sums["rest"] += rest
                # Tally by ship and region
                ship = row['ship_type'].strip()
                region = row['region'].strip()
                by_ship[ship] = by_ship.get(ship, 0) + 1
                by_region[region] = by_region.get(region, 0) + 1
    # Calculate averages
    averages = {
        "sleepHours": round(sums["sleep"] / totals["submissions"], 2) if totals["submissions"] else 0,
        "restViolations": round(sums["rest"] / totals["submissions"], 2) if totals["submissions"] else 0,
    }
    metrics = {
        "totals": totals,
        "averages": averages,
        "byShip": by_ship,
        "byRegion": by_region,
        "updatedAt": datetime.now(timezone.utc).isoformat()
    }
    return metrics

def main():
    base_dir = Path(__file__).resolve().parents[1]
    submissions_path = base_dir / 'submissions'
    data_path = base_dir / 'data' / 'data.json'
    submissions_path.mkdir(exist_ok=True)
    data_path.parent.mkdir(exist_ok=True)
    metrics = aggregate_submissions(submissions_path)
    with data_path.open('w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2)
    print(f"Aggregated {metrics['totals']['submissions']} submissions into {data_path}")

if __name__ == '__main__':
    main()