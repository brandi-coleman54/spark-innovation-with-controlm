#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def process_credit(pnr):
    # 95% success
    return random.random() < 0.95

def main():
    parser = argparse.ArgumentParser(description="Issue refund or travel voucher/credit")
    parser.add_argument("--pnr", required=True, help="Passenger PNR")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Issuing travel credit/refund for {args.pnr} ...")
    time.sleep(1)

    if process_credit(args.pnr):
        print(f"[{datetime.now().isoformat()}] Travel credit/refund issued for {args.pnr}.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Credit/refund FAILED for {args.pnr}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
