#!/usr/bin/env python3
import argparse, time; p=argparse.ArgumentParser()
p.add_argument("--run", required=True); p.add_argument("--workspace", required=True); p.add_argument("--jobs", required=True)
args=p.parse_args(); time.sleep(1)
print(f"AUDIT run={args.run} workspace={args.workspace} jobs={args.jobs}")
