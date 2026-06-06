#!/usr/bin/env python3
"""Send sold-book metadata to a single Top-N reducer."""

import json
import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) < 14:
        continue
    try:
        sold_count = int(float(fields[13]))
    except ValueError:
        continue
    payload = {
        "book_id": fields[0],
        "source": fields[1],
        "title": fields[2],
        "author": fields[3],
        "main_category": fields[6],
        "sold_count": sold_count,
    }
    print(f"top\t{json.dumps(payload, ensure_ascii=False)}")
