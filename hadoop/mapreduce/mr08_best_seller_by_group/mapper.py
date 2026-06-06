#!/usr/bin/env python3
"""Emit each book for author, publisher and category best-seller groups."""

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
        "publisher": fields[4],
        "main_category": fields[6],
        "sold_count": sold_count,
    }
    for group_type, group_value in (
        ("author", fields[3]),
        ("publisher", fields[4]),
        ("category", fields[6]),
    ):
        if group_value and group_value != "Unknown":
            output = {**payload, "group_type": group_type, "group_value": group_value}
            print(f"{group_type}::{group_value}\t{json.dumps(output, ensure_ascii=False)}")
