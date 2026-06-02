#!/usr/bin/env python3
"""Emit one count per language group."""

import sys


for line in sys.stdin:
    fields = line.rstrip("\n").split("\t")
    if len(fields) >= 6 and fields[5]:
        print(f"{fields[5]}\t1")
