#!/usr/bin/env python3
import argparse
import random
import sys
import time
from datetime import datetime

def check_resources(order_id):
    """
    Simulate checking both inventory and staffing for a given order.
    Returns a tuple: (inventory_ok, staffing_ok).
    """
    # Simulate some logic (95% chance everything is fine)
    inventory_ok = random.random() < 0.95  # 95% chance inventory is available
    staffing_ok = random.random() < 0.95  # 95% chance staff is available

    return inventory_ok, staffing_ok

def main():
    parser = argparse.ArgumentParser(description="Check inventory and staffing for order")
    parser.add_argument("order_id", help="Order ID to validate resources")
    args = parser.parse_args()

    order_id = args.order_id

    print(f"[{datetime.now().isoformat()}] Checking inventory and staffing for order {order_id}...")
    time.sleep(1)  # Simulate lookup delay

    inventory_ok, staffing_ok = check_resources(order_id)

    # Log results to stdout (captured by Control-M)
    if inventory_ok and staffing_ok:
        print(f"[{datetime.now().isoformat()}] Order {order_id}: Inventory and staffing are sufficient.")
        result = 0
    else:
        if not inventory_ok and not staffing_ok:
            print(f"[{datetime.now().isoformat()}] Order {order_id}: Insufficient inventory AND staffing!")
        elif not inventory_ok:
            print(f"[{datetime.now().isoformat()}] Order {order_id}: Insufficient inventory!")
        elif not staffing_ok:
            print(f"[{datetime.now().isoformat()}] Order {order_id}: Insufficient staffing!")
        result = 1

    # Write a log file for debugging/audit
    with open(f"/tmp/order_{order_id}_resources.log", "a") as log_file:
        log_file.write(f"{datetime.now().isoformat()} - Inventory OK: {inventory_ok}, Staffing OK: {staffing_ok}\n")

    # Exit with appropriate status code
    sys.exit(result)

if __name__ == "__main__":
    main()
