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
from collections import defaultdict
import re

def extract_date_from_filename(filename: str) -> str:
    """Extract date from filename format: YYYYMMDD_HHMMSS_*.csv
    Returns date in YYYY-MM-DD format, or None if not found.
    """
    match = re.match(r'(\d{4})(\d{2})(\d{2})_', filename)
    if match:
        year, month, day = match.groups()
        return f"{year}-{month}-{day}"
    return None

def aggregate_submissions(submissions_path: Path) -> dict:
    totals = {"submissions": 0}
    sums = {"sleep": 0.0, "rest": 0.0}
    by_ship = {}
    by_region = {}
    
    # Time-series data for trends
    daily_data = defaultdict(lambda: {"count": 0, "sleep_sum": 0.0, "rest_sum": 0.0})
    
    # Iterate through all CSV files
    for csv_file in submissions_path.glob("*.csv"):
        # Extract date from filename
        submission_date = extract_date_from_filename(csv_file.name)
        
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
                
                # Add to time-series data
                if submission_date:
                    daily_data[submission_date]["count"] += 1
                    daily_data[submission_date]["sleep_sum"] += sleep
                    daily_data[submission_date]["rest_sum"] += rest
                
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
    
    # Prepare time-series data for charts
    trends = []
    for date in sorted(daily_data.keys()):
        data = daily_data[date]
        trends.append({
            "date": date,
            "submissions": data["count"],
            "avgSleep": round(data["sleep_sum"] / data["count"], 2) if data["count"] > 0 else 0,
            "avgRestViolations": round(data["rest_sum"] / data["count"], 2) if data["count"] > 0 else 0
        })
    
    metrics = {
        "totals": totals,
        "averages": averages,
        "byShip": by_ship,
        "byRegion": by_region,
        "trends": trends,
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
