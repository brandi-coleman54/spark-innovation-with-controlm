#!/usr/bin/env python3
import argparse, sys, time, json
from datetime import datetime

def validate_application(app_id, customer_id):
    # Simulate basic validation (95% pass)
    return {"valid": True, "reasons": []} if hash(app_id+customer_id) % 20 != 0 else {"valid": False, "reasons": ["Missing document: income_proof"]}

def main():
    parser = argparse.ArgumentParser(description="Validate and log incoming credit card application")
    parser.add_argument("--application", required=True, help="Application ID")
    parser.add_argument("--customer", required=True, help="Customer ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Intake received for application {args.application} (customer {args.customer})...")
    time.sleep(1)
    result = validate_application(args.application, args.customer)

    if result["valid"]:
        print(f"[{datetime.now().isoformat()}] Application {args.application} intake successful.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Application {args.application} intake FAILED. Reasons: {', '.join(result['reasons'])}")
        sys.exit(1)

if __name__ == "__main__":
    main()
