#!/usr/bin/env python3
"""Emit one count per main category."""

import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) >= 7 and fields[6]:
        print(f"{fields[6]}\t1")
