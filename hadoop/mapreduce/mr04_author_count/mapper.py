#!/usr/bin/env python3
"""Emit one count per author."""

import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) >= 4 and fields[3]:
        print(f"{fields[3]}\t1")
