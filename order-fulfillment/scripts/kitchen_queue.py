#!/usr/bin/env python3
import argparse
import random
import sys
import time
from datetime import datetime

def queue_order(order_id):
    """
    Simulate placing an order into the kitchen queue.
    Returns True if queued successfully, False otherwise.
    """
    # Simulate a 95% success rate for queuing
    success = random.random() < 0.95
    return success

def main():
    parser = argparse.ArgumentParser(description="Queue order in kitchen system and update tracker")
    parser.add_argument("--order", required=True, help="Order ID to queue")
    args = parser.parse_args()

    order_id = args.order

    print(f"[{datetime.now().isoformat()}] Attempting to queue order {order_id} in kitchen systems...")
    time.sleep(1)  # Simulate queueing delay

    if queue_order(order_id):
        print(f"[{datetime.now().isoformat()}] Order {order_id} successfully queued in kitchen systems.")
        # Log for Control-M to track
        with open(f"/tmp/order_{order_id}_kitchen.log", "a") as log_file:
            log_file.write(f"{datetime.now().isoformat()} - Queued successfully in kitchen.\n")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] FAILED to queue order {order_id} in kitchen systems!")
        with open(f"/tmp/order_{order_id}_kitchen.log", "a") as log_file:
            log_file.write(f"{datetime.now().isoformat()} - FAILED to queue in kitchen.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
