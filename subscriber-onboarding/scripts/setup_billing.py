#!/usr/bin/env python3
import argparse, sys, time, random
from datetime import datetime

def setup_billing_account(act_id):
    # 90% success to create billing account
    return random.random() < 0.9

def main():
    parser = argparse.ArgumentParser(description="Set up billing account for subscriber")
    parser.add_argument("--activation", required=True, help="Activation ID")
    args = parser.parse_args()

    aid = args.activation
    print(f"[{datetime.now().isoformat()}] Setting up billing account for activation {aid}...")
    time.sleep(1)

    if setup_billing_account(aid):
        print(f"[{datetime.now().isoformat()}] Billing account successfully created for {aid}.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] FAILED to set up billing for {aid}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
