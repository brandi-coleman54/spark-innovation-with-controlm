#!/usr/bin/env python3

import os, json, time, argparse
p=argparse.ArgumentParser(); p.add_argument("--region", default="NA"); args=p.parse_args()
time.sleep(1)
print(json.dumps({"stage":"ingest","region":args.region,"rows":125000}))
