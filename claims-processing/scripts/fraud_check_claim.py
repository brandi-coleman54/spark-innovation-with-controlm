#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def run_fraud_check(claim_id):
    return random.random() < 0.1  # 10% chance fraud suspected

def main():
    parser = argparse.ArgumentParser(description="Perform fraud risk scoring for the claim")
    parser.add_argument("--claim", required=True, help="Claim ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Running fraud check for {args.claim}...")
    time.sleep(1)

    if run_fraud_check(args.claim):
        print(f"[{datetime.now().isoformat()}] FRAUD ALERT: Claim {args.claim} flagged for manual review!")
        sys.exit(1)
    else:
        print(f"[{datetime.now().isoformat()}] Claim {args.claim} passed fraud screening.")
        sys.exit(0)

if __name__ == "__main__":
    main()
