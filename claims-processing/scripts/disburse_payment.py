#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def process_payout(claim_id):
    return random.random() < 0.95  # 95% chance payment succeeds

def main():
    parser = argparse.ArgumentParser(description="Process payment for approved claim")
    parser.add_argument("--claim", required=True, help="Claim ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Initiating payment for claim {args.claim}...")
    time.sleep(1)

    if process_payout(args.claim):
        print(f"[{datetime.now().isoformat()}] Payment disbursed for claim {args.claim}.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Payment FAILED for claim {args.claim}.")
        sys.exit(1)

if __name__ == "__main__":
    main()

