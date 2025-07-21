#!/usr/bin/env python3
import argparse
import time
import random

def check_order_status(order_id):
    """
    Simulate checking or updating the delivery status of an order.
    In a real app, this might query a database or API.
    """
    statuses = [
        "Order received",
        "Preparing your order",
        "Baking in the oven",
        "Out for delivery",
        "Delivered"
    ]
    # Simulate random status
    status = random.choice(statuses)
    return status

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description="Update or check Domino's order status")
    parser.add_argument("--order", required=True, help="Order ID to update/check")
    args = parser.parse_args()

    order_id = args.order

    # Simulate processing
    print(f"Checking delivery status for order {order_id}...")
    time.sleep(2)  # simulate a delay for realism

    status = check_order_status(order_id)
    print(f"Order {order_id} status: {status}")

    # Here you could also:
    # - Write to a log
    # - Send the status to Control-M for job completion
    # - Update a database/API

if __name__ == "__main__":
    main()
