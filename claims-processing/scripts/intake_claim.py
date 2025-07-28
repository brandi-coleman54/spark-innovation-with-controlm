#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def validate_claim(claim_id):
    return random.random() < 0.95  # 95% chance claim data is valid

def main():
    parser = argparse.ArgumentParser(description="Validate and log incoming claim request")
    parser.add_argument("--claim", required=True, help="Claim ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Validating claim {args.claim}...")
    time.sleep(1)

    if validate_claim(args.claim):
        print(f"[{datetime.now().isoformat()}] Claim {args.claim} intake successful.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Claim {args.claim} intake FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()

