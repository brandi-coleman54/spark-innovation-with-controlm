#!/usr/bin/env python3
import argparse
import random
import sys
import time
from datetime import datetime

def process_payment(order_id):
    """
    Simulate payment processing.
    Returns True if payment succeeds, False otherwise.
    """
    # 90% chance payment succeeds
    return random.random() < 0.9

def fraud_check(order_id):
    """
    Simulate a basic fraud check.
    Returns True if order is flagged (fraud suspected), False otherwise.
    """
    # 5% chance fraud is suspected
    return random.random() < 0.05

def log_transaction(order_id, status):
    """
    Log the payment transaction status to a file for audit.
    """
    with open(f"/tmp/order_{order_id}_payment.log", "a") as log_file:
        log_file.write(f"{datetime.now().isoformat()} - Payment Status: {status}\n")

def main():
    parser = argparse.ArgumentParser(description="Automate payment, fraud check, and transaction logging")
    parser.add_argument("--order", required=True, help="Order ID to process payment for")
    args = parser.parse_args()

    order_id = args.order

    print(f"[{datetime.now().isoformat()}] Starting payment process for order {order_id}...")
    time.sleep(1)  # Simulate processing delay

    if not process_payment(order_id):
        print(f"[{datetime.now().isoformat()}] Payment FAILED for order {order_id}.")
        log_transaction(order_id, "FAILED")
        sys.exit(1)

    print(f"[{datetime.now().isoformat()}] Payment approved for order {order_id}. Running fraud check...")
    time.sleep(1)  # Simulate fraud check delay

    if fraud_check(order_id):
        print(f"[{datetime.now().isoformat()}] FRAUD ALERT: Order {order_id} flagged for review!")
        log_transaction(order_id, "FLAGGED_FOR_REVIEW")
        sys.exit(1)

    print(f"[{datetime.now().isoformat()}] Payment cleared and logged for order {order_id}.")
    log_transaction(order_id, "APPROVED")
    sys.exit(0)

if __name__ == "__main__":
    main()
