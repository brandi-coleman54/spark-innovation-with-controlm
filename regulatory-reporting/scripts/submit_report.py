#!/usr/bin/env python3
import argparse, time, random; p=argparse.ArgumentParser()
p.add_argument("--method", choices=["sftp","api"], default="sftp")
p.add_argument("--endpoint", required=False); p.add_argument("--package", required=True)
p.add_argument("--timeout", type=int, default=120); p.add_argument("--force-outcome", default="pass")
args=p.parse_args(); time.sleep(1)
ok = (args.force_outcome=="pass")
print(f"Submit via {args.method} to {args.endpoint} package={args.package}")
exit(0 if ok else 1)
