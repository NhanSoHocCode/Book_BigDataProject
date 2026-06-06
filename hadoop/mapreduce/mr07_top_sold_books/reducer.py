#!/usr/bin/env python3
"""Return the globally best-selling books."""

import heapq
import json
import os
import sys


limit = int(os.getenv("TOP_N", "20"))
top = []
sequence = 0
for line in sys.stdin:
    _, raw_payload = line.rstrip("\n").split("\t", 1)
    payload = json.loads(raw_payload)
    entry = (int(payload["sold_count"]), sequence, payload)
    sequence += 1
    if len(top) < limit:
        heapq.heappush(top, entry)
    else:
        heapq.heappushpop(top, entry)

for rank, (_, _, payload) in enumerate(sorted(top, reverse=True), start=1):
    payload["rank"] = rank
    print(f"{rank}\t{json.dumps(payload, ensure_ascii=False)}")
