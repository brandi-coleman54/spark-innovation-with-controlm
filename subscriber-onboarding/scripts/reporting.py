#!/usr/bin/env python3
import argparse
import sys
import time
from datetime import datetime
import random
import json
import os

def fetch_sales_data(report_date):
    """
    Simulate fetching sales data for the given date.
    Returns a dictionary with dummy metrics.
    """
    return {
        "total_orders": random.randint(500, 1000),
        "total_sales": round(random.uniform(5000, 15000), 2),
        "average_order_value": round(random.uniform(10, 25), 2)
    }

def fetch_ops_data(report_date):
    """
    Simulate fetching operational metrics for the given date.
    """
    return {
        "on_time_deliveries": f"{random.randint(85, 100)}%",
        "kitchen_throughput": random.randint(400, 900),
        "staffing_level": f"{random.randint(70, 100)}%"
    }

def generate_dashboard_file(report_date, sales_data, ops_data):
    """
    Save aggregated metrics into a JSON file for dashboards.
    """
    report = {
        "report_date": report_date,
        "sales_metrics": sales_data,
        "operations_metrics": ops_data,
        "generated_at": datetime.now().isoformat()
    }

    output_dir = "/tmp/dominos_reports"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/dashboard_{report_date}.json"

    with open(output_file, "w") as f:
        json.dump(report, f, indent=4)

    return output_file

def main():
    parser = argparse.ArgumentParser(description="Aggregate sales and ops data for dashboards")
    parser.add_argument("--date", required=True, help="Report date in YYYY-MM-DD format")
    args = parser.parse_args()

    report_date = args.date

    print(f"[{datetime.now().isoformat()}] Generating report for {report_date}...")
    time.sleep(1)

    # Simulate fetching and aggregating
    sales_data = fetch_sales_data(report_date)
    ops_data = fetch_ops_data(report_date)

    # Generate dashboard JSON
    output_file = generate_dashboard_file(report_date, sales_data, ops_data)

    print(f"[{datetime.now().isoformat()}] Report generated at {output_file}")
    sys.exit(0)

if __name__ == "__main__":
    main()
