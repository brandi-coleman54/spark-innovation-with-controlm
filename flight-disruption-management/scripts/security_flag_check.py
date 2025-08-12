#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def run_security_check(flight_id, pnr):
    # 8% chance the PNR is flagged for manual review
    return random.random() < 0.08

def main():
    parser = argparse.ArgumentParser(description="Screen for security flags or ticketing anomalies")
    parser.add_argument("--flight", required=True, help="Flight number")
    parser.add_argument("--pnr", required=True, help="Passenger PNR")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Running security/anomaly check for {args.flight} / {args.pnr} ...")
    time.sleep(1)

    flagged = run_security_check(args.flight, args.pnr)
    if flagged:
        print(f"[{datetime.now().isoformat()}] ALERT: {args.pnr} flagged for manual review.")
        sys.exit(1)
    else:
        print(f"[{datetime.now().isoformat()}] {args.pnr} passed security/anomaly screening.")
        sys.exit(0)

if __name__ == "__main__":
    main()
