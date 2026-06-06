#!/usr/bin/env python3
"""Sum book counts by source."""

import sys


current_key = None
total = 0
for line in sys.stdin:
    key, value = line.rstrip("\n").split("\t", 1)
    if current_key is not None and key != current_key:
        print(f"{current_key}\t{total}")
        total = 0
    current_key = key
    total += int(value)
if current_key is not None:
    print(f"{current_key}\t{total}")
