#!/usr/bin/env python3
"""Calculate average book price by category."""

import sys


current_key = None
total = 0.0
count = 0
for line in sys.stdin:
    key, value = line.rstrip("\n").split("\t", 1)
    if current_key is not None and key != current_key:
        print(f"{current_key}\t{total / count:.2f}")
        total = 0.0
        count = 0
    current_key = key
    total += float(value)
    count += 1
if current_key is not None and count:
    print(f"{current_key}\t{total / count:.2f}")
