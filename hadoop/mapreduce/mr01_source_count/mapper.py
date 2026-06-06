#!/usr/bin/env python3
"""Emit one count per book source."""

import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) >= 2 and fields[1]:
        print(f"{fields[1]}\t1")
