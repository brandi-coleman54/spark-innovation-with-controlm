#!/usr/bin/env python3
import argparse
import random
import sys
import time
from datetime import datetime

def validate_customer(customer_id):
    """
    Simulate validating a customer in the mobile app system.
    Returns True if valid, False otherwise.
    """
    # 90% chance customer is valid
    return random.random() < 0.9

def route_order(customer_id):
    """
    Simulate routing the order (kitchen, pickup, or delivery).
    Returns a route string if successful, None if failed.
    """
    routes = ["Kitchen", "Pickup Counter", "Delivery Queue"]
    # 95% chance routing succeeds
    if random.random() < 0.95:
        return random.choice(routes)
    return None

def main():
    parser = argparse.ArgumentParser(description="Validate and route order from mobile app")
    parser.add_argument("--customer", required=True, help="Customer ID placing the order")
    args = parser.parse_args()

    customer_id = args.customer

    print(f"[{datetime.now().isoformat()}] Validating customer {customer_id}...")
    time.sleep(1)

    if not validate_customer(customer_id):
        print(f"[{datetime.now().isoformat()}] Customer {customer_id} validation FAILED!")
        with open(f"/tmp/customer_{customer_id}_order.log", "a") as log_file:
            log_file.write(f"{datetime.now().isoformat()} - Validation FAILED.\n")
        sys.exit(1)

    print(f"[{datetime.now().isoformat()}] Customer {customer_id} validated. Routing order...")
    time.sleep(1)

    route = route_order(customer_id)
    if route:
        print(f"[{datetime.now().isoformat()}] Order for customer {customer_id} routed to: {route}")
        with open(f"/tmp/customer_{customer_id}_order.log", "a") as log_file:
            log_file.write(f"{datetime.now().isoformat()} - Routed to {route}.\n")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] FAILED to route order for customer {customer_id}!")
        with open(f"/tmp/customer_{customer_id}_order.log", "a") as log_file:
            log_file.write(f"{datetime.now().isoformat()} - Routing FAILED.\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
