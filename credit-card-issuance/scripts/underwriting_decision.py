#!/usr/bin/env python3
import argparse, sys, time, random, re
from datetime import datetime

def decide(app_id, score=None):
    # Simple rules + randomness: approve if score >= 680; else 25% chance approve
    if score is None:
        random.seed(hash(app_id) % 10_000_000)
        score = random.randint(520, 820)
    approved = score >= 680 or (score < 680 and random.random() < 0.25)
    limit = (score - 600) * 50 if approved else 0
    return approved, score, max(1000, int(limit)) if approved else 0

def main():
    parser = argparse.ArgumentParser(description="Automated underwriting rules; emits decision")
    parser.add_argument("--application", required=True, help="Application ID")
    parser.add_argument("--score", type=int, help="Optional known credit score")
    args = parser.parse_args()

    print(f"[{datetime.now().isoformat()}] Running underwriting for {args.application}...")
    time.sleep(1)
    approved, score, limit = decide(args.application, args.score)
    if approved:
        print(f"[{datetime.now().isoformat()}] APPROVED application {args.application}; score={score}; credit_limit={limit}")
        sys.exit(0)
    else:
        print(f"[{datetime.now().isoformat()}] DECLINED application {args.application}; score={score}")
        sys.exit(1)

if __name__ == "__main__":
    main()
