#!/usr/bin/env python3
"""Emit book metadata for maximum-price calculation by category."""

import json
import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) < 9 or not fields[6]:
        continue
    try:
        price = float(fields[8])
    except ValueError:
        continue
    payload = {
        "main_category": fields[6],
        "book_id": fields[0],
        "source": fields[1],
        "title": fields[2],
        "author": fields[3],
        "price": price,
    }
    print(f"{fields[6]}\t{json.dumps(payload, ensure_ascii=False)}")
