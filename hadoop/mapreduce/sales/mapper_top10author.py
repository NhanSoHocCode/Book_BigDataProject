#!/usr/bin/env python3

import sys

def parse_line(line):

    cols = line.rstrip("\n").split("\t")

    if len(cols) < 11:
        return None

    return {
        "book_id": cols[0].strip(),
        "source": cols[1].strip(),
        "title": cols[2].strip(),
        "author": cols[3].strip(),
        "publisher": cols[4].strip(),
        "language_group": cols[5].strip(),
        "main_category": cols[6].strip(),
        "price": cols[7].strip(),
        "rating": cols[8].strip(),
        "review_count": cols[9].strip(),
        "sold_count": cols[10].strip()
    }

def safe_float(value):
    try:
        return float(value)
    except:
        return 0.0

def safe_int(value):
    try:
        return int(float(value))
    except:
        return 0

for line in sys.stdin:
    book = parse_line(line)

    if not book:
        continue

    sold = safe_int(book["sold_count"])
    author = book["author"]

    if author:
        print(f"{author}\t{sold}")
