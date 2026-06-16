#!/usr/bin/env python3

import sys
import heapq

current_author = None
total_sold = 0

top_authors = []

for line in sys.stdin:

    author, sold = line.strip().split("\t")

    sold = int(sold)

    if current_author == author:

        total_sold += sold

    else:

        if current_author:

            heapq.heappush(
                top_authors,
                (
                    total_sold,
                    current_author
                )
            )

            if len(top_authors) > 10:

                heapq.heappop(top_authors)

        current_author = author
        total_sold = sold

if current_author:

    heapq.heappush(
        top_authors,
        (
            total_sold,
            current_author
        )
    )

    if len(top_authors) > 10:

        heapq.heappop(top_authors)


for sold, author in sorted(
    top_authors,
    reverse=True
):

    print(
        f"{author}\t{sold}"
    )