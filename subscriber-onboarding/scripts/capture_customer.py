#!/usr/bin/env python3
import argparse, sys, time, random
from datetime import datetime

def validate_customer(customer_id):
    # Simulate KYC (Know Your Customer) validation (90% success)
    return random.random() < 0.9

def main():
    parser = argparse.ArgumentParser(description="Validate new mobile subscriber request")
    parser.add_argument("--customer", required=True, help="Customer ID for onboarding")
    args = parser.parse_args()

    cid = args.customer
    print(f"[{datetime.now().isoformat()}] Starting KYC validation for customer {cid}...")
    time.sleep(1)

    if not validate_customer(cid):
        print(f"[{datetime.now().isoformat()}] Customer {cid} KYC FAILED.")
        with open(f"/tmp/customer_{cid}_onboarding.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - KYC FAILED\n")
        sys.exit(1)

    print(f"[{datetime.now().isoformat()}] Customer {cid} KYC PASSED. Proceeding to credit check.")
    with open(f"/tmp/customer_{cid}_onboarding.log", "a") as f:
        f.write(f"{datetime.now().isoformat()} - KYC PASSED\n")
    sys.exit(0)

if __name__ == "__main__":
    main()
