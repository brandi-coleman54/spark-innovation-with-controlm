#!/usr/bin/env python3
import argparse, sys, time, random
from datetime import datetime

def provision(app_id):
    # 98% success
    return random.random() < 0.98

def main():
    parser = argparse.ArgumentParser(description="Provision digital card and queue physical card printing")
    parser.add_argument("--application", required=True, help="Application ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Provisioning card for {args.application} (tokenization + wallet push)...")
    time.sleep(1)
    ok = provision(args.application)
    if ok:
        print(f"[{datetime.now().isoformat()}] Digital card provisioned; physical card queued for print & mail.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] Card provisioning FAILED for application {args.application}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
