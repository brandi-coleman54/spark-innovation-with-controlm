#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def validate_ticket(pnr):
    # 90% chance ticket is eligible for rebooking/refund
    return random.random() < 0.9

def main():
    parser = argparse.ArgumentParser(description="Validate fare class, refund/change eligibility, and interline rules")
    parser.add_argument("pnr", help="Passenger PNR")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Validating ticket rules for PNR {args.pnr} ...")
    time.sleep(1)

    if validate_ticket(args.pnr):
        print(f"[{datetime.now().isoformat()}] Ticket for {args.pnr} is eligible.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Ticket for {args.pnr} is NOT eligible.")
        sys.exit(1)

if __name__ == "__main__":
    main()
