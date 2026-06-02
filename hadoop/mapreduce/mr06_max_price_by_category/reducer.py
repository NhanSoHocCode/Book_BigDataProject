#!/usr/bin/env python3
"""Keep the most expensive book in each category."""

import json
import sys


current_key = None
winner = None
for line in sys.stdin:
    key, raw_payload = line.rstrip("\n").split("\t", 1)
    if current_key is not None and key != current_key:
        print(f"{current_key}\t{json.dumps(winner, ensure_ascii=False)}")
        winner = None
    current_key = key
    payload = json.loads(raw_payload)
    if winner is None or payload["price"] > winner["price"]:
        winner = payload
if current_key is not None and winner is not None:
    print(f"{current_key}\t{json.dumps(winner, ensure_ascii=False)}")
