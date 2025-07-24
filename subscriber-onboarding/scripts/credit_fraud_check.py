#!/usr/bin/env python3
import argparse, sys, time, random
from datetime import datetime

def run_credit_check(act_id):
    # 85% pass credit check
    return random.random() < 0.85

def fraud_check(act_id):
    # 3% chance of fraud flag
    return random.random() < 0.03

def main():
    parser = argparse.ArgumentParser(description="Run credit and fraud checks for new subscriber")
    parser.add_argument("--activation", required=True, help="Activation ID")
    args = parser.parse_args()

    aid = args.activation
    print(f"[{datetime.now().isoformat()}] Running credit and fraud checks for activation {aid}...")
    time.sleep(1)

    if not run_credit_check(aid):
        print(f"[{datetime.now().isoformat()}] CREDIT CHECK FAILED for activation {aid}.")
        sys.exit(1)

    if fraud_check(aid):
        print(f"[{datetime.now().isoformat()}] FRAUD ALERT for activation {aid}! Flagged for review.")
        sys.exit(1)

    print(f"[{datetime.now().isoformat()}] Credit and fraud checks PASSED for activation {aid}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
