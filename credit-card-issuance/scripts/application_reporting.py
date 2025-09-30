#!/usr/bin/env python3
import argparse, sys, time, os, json, random
from datetime import datetime

def generate_metrics(date_str):
    return {
        "applications_received": random.randint(300, 1200),
        "approved": random.randint(150, 900),
        "declined": random.randint(50, 300),
        "kyc_flags": random.randint(0, 40),
        "avg_credit_score": random.randint(600, 740),
        "avg_credit_limit": random.randint(1500, 12000)
    }

def main():
    parser = argparse.ArgumentParser(description="Aggregate daily credit card issuance metrics")
    parser.add_argument("--date", required=True, help="Report date in YYYY-MM-DD")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Generating issuance report for {args.date}...")
    time.sleep(1)
    data = generate_metrics(args.date)

    outdir = "/tmp/credit_card_reports"
    os.makedirs(outdir, exist_ok=True)
    out = f"{outdir}/issuance_{args.date}.json"
    with open(out, "w") as f:
        json.dump({"date": args.date, "metrics": data, "generated_at": datetime.now().isoformat()}, f, indent=2)
    print(f"[{datetime.now().isoformat()}] Report saved at {out}")
    sys.exit(0)

if __name__ == "__main__":
    main()
