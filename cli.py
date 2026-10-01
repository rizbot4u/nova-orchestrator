#!/usr/bin/env python3
import sys, json, httpx
if len(sys.argv) < 2: print("usage: python cli.py 'prompt'"); sys.exit(1)
r = httpx.post("http://127.0.0.1:8010/orchestrate", json={"prompt": " ".join(sys.argv[1:])}, timeout=60)
print(json.dumps(r.json(), indent=2))
