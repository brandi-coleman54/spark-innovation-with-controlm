#!/usr/bin/env python3
import argparse, sys, time, random
from datetime import datetime

def provision_services(act_id):
    # Simulate SIM activation (95% success)
    return random.random() < 0.95

def main():
    parser = argparse.ArgumentParser(description="Provision SIM card and configure services")
    parser.add_argument("--activation", required=True, help="Activation ID")
    args = parser.parse_args()

    aid = args.activation
    print(f"[{datetime.now().isoformat()}] Activating SIM and provisioning services for activation {aid}...")
    time.sleep(2)

    if provision_services(aid):
        print(f"[{datetime.now().isoformat()}] SIM and services successfully provisioned for {aid}.")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] FAILED to provision SIM/services for {aid}.")
        sys.exit(1)

if __name__ == "__main__":
    main()
