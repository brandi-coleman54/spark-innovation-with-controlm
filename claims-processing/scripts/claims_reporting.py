#!/usr/bin/env python3
import argparse, sys, time, random, json, os
from datetime import datetime

def generate_report(date):
    return {
        "claims_processed": random.randint(100, 500),
        "payout_total": round(random.uniform(100000, 500000), 2),
        "fraud_flags": random.randint(0, 10)
    }

def main():
    parser = argparse.ArgumentParser(description="Aggregate processed claims data for dashboards")
    parser.add_argument("--date", required=True, help="Report date in YYYY-MM-DD format")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Generating claims report for {args.date}...")
    time.sleep(1)
    data = generate_report(args.date)

    output_dir = "/tmp/claims_reports"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/claims_{args.date}.json"
    with open(output_file, "w") as f:
        json.dump({"date": args.date, "metrics": data, "generated_at": datetime.now().isoformat()}, f, indent=4)

    print(f"[{datetime.now().isoformat()}] Claims report saved at {output_file}")
    sys.exit(0)

if __name__ == "__main__":
    main()

