#!/usr/bin/env python3
import argparse, sys, time, json, random
from datetime import datetime

def kyc_screen(customer_id):
    # 7% chance to flag
    flagged = random.random() < 0.07
    return {"flagged": flagged, "lists": ["OFAC","PEP"] if flagged else []}

def main():
    parser = argparse.ArgumentParser(description="Perform KYC/AML screening")
    parser.add_argument("--customer", required=True, help="Customer ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Running KYC/AML checks for {args.customer}...")
    time.sleep(1)
    result = kyc_screen(args.customer)

    if result["flagged"]:
        print(f"[{datetime.now().isoformat()}] KYC/AML FLAG for {args.customer} on lists: {', '.join(result['lists'])}")
        sys.exit(1)  # non-zero signals manual review path
    else:
        print(f"[{datetime.now().isoformat()}] {args.customer} passed KYC/AML screening.")
        sys.exit(0)

if __name__ == "__main__":
    main()
