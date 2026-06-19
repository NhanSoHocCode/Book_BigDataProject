#!/usr/bin/env python3

import sys
import heapq

top_books = []

for line in sys.stdin:

    sold, title, author = line.strip().split("\t")

    sold = int(sold)

    heapq.heappush(
        top_books,
        (sold, title, author)
    )

    if len(top_books) > 10:
        heapq.heappop(top_books)

for sold, title, author in sorted(
    top_books,
    reverse=True
):

    print(
        f"{title}\t{author}\t{sold}"
    )