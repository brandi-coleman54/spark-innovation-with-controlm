#!/usr/bin/env python3
import argparse, sys, time, random, json
from datetime import datetime

def fetch_credit_score(app_id):
    random.seed(hash(app_id) % 10_000_000)
    score = random.randint(520, 820)
    return score

def main():
    parser = argparse.ArgumentParser(description="Check applicant's credit score via external bureau")
    parser.add_argument("--application", required=True, help="Application ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Requesting credit score for application {args.application}...")
    time.sleep(1)
    score = fetch_credit_score(args.application)
    print(f"[{datetime.now().isoformat()}] Credit score for {args.application}: {score}")
    # exit 0 regardless; underwriting will interpret score via log capture
    sys.exit(0)

if __name__ == "__main__":
    main()
