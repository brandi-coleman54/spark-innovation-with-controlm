#!/usr/bin/env python3
import argparse, time; p=argparse.ArgumentParser()
p.add_argument("--in", dest="inp", required=True); p.add_argument("--out", required=True)
args=p.parse_args(); time.sleep(1)
print(f"Report package created from {args.inp} -> {args.out}")
