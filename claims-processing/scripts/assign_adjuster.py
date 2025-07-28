#!/usr/bin/env python3
import argparse, time, random, sys
from datetime import datetime

def queue_adjuster(claim_id):
    return random.choice(["Human Adjuster", "Auto-Approved"])

def main():
    parser = argparse.ArgumentParser(description="Queue claim for adjuster review or auto-approval")
    parser.add_argument("--claim", required=True, help="Claim ID")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Assigning adjuster for claim {args.claim}...")
    time.sleep(1)
    route = queue_adjuster(args.claim)
    print(f"[{datetime.now().isoformat()}] Claim {args.claim} routed to: {route}")
    sys.exit(0)

if __name__ == "__main__":
    main()
