#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def route_case(pnr):
    return random.choice(["Human Agent", "Auto-Rebooked"])

def main():
    parser = argparse.ArgumentParser(description="Route passenger to human agent or automated rebooking")
    parser.add_argument("--pnr", required=True, help="Passenger PNR")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Assigning rebooking path for {args.pnr} ...")
    time.sleep(1)
    route = route_case(args.pnr)
    print(f"[{datetime.now().isoformat()}] {args.pnr} routed to: {route}")
    sys.exit(0)

if __name__ == "__main__":
    main()
