#!/usr/bin/env python3
"""Emit category and price for average calculation."""

import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) < 9 or not fields[6]:
        continue
    try:
        price = float(fields[8])
    except ValueError:
        continue
    print(f"{fields[6]}\t{price}")
