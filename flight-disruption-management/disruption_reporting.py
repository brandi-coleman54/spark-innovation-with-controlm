#!/usr/bin/env python3
import argparse, sys, time, random, json, os
from datetime import datetime

def generate_report(date):
    return {
        "disruptions_processed": random.randint(10, 120),
        "passengers_rebooked": random.randint(50, 800),
        "credits_issued_total": round(random.uniform(10000, 250000), 2),
        "manual_reviews": random.randint(0, 40)
    }

def main():
    parser = argparse.ArgumentParser(description="Aggregate flight disruption metrics for dashboards")
    parser.add_argument("--date", required=True, help="Report date in YYYY-MM-DD format")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Generating airline disruption report for {args.date} ...")
    time.sleep(1)
    data = generate_report(args.date)

    output_dir = "/tmp/airline_reports"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/disruptions_{args.date}.json"
    with open(output_file, "w") as f:
        json.dump({"date": args.date, "metrics": data, "generated_at": datetime.now().isoformat()}, f, indent=4)

    print(f"[{datetime.now().isoformat()}] Disruption report saved at {output_file}")
    sys.exit(0)

if __name__ == "__main__":
    main()
