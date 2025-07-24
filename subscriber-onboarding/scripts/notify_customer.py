#!/usr/bin/env python3
import argparse, time, random
from datetime import datetime

def send_notification(cid):
    statuses = [
        "Activation successful",
        "Welcome SMS sent",
        "Email confirmation sent",
        "Customer notified of SIM activation"
    ]
    return random.choice(statuses)

def main():
    parser = argparse.ArgumentParser(description="Notify customer about activation status")
    parser.add_argument("--customer", required=True, help="Customer ID")
    args = parser.parse_args()

    cid = args.customer
    print(f"[{datetime.now().isoformat()}] Sending notification to customer {cid}...")
    time.sleep(1)
    status = send_notification(cid)
    print(f"[{datetime.now().isoformat()}] Notification status for customer {cid}: {status}")

if __name__ == "__main__":
    main()
