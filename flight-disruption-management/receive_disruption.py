#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def capture_event(flight_id, pnr):
    # 97% chance intake is successful
    return random.random() < 0.97

def main():
    parser = argparse.ArgumentParser(description="Capture flight disruption event and affected passenger list")
    parser.add_argument("--flight", required=True, help="Flight number (e.g., AA1234)")
    parser.add_argument("--pnr", required=True, help="Passenger PNR")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Receiving disruption notice for flight {args.flight}, PNR {args.pnr} ...")
    time.sleep(1)

    if capture_event(args.flight, args.pnr):
        print(f"[{datetime.now().isoformat()}] Disruption intake successful for {args.flight} / {args.pnr}.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Disruption intake FAILED for {args.flight} / {args.pnr}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
