#!/usr/bin/env python3

import sys

categories = {}

for line in sys.stdin:

    try:

        category, rating, title, author = (
            line.rstrip("\n").split("\t")
        )

        rating = float(rating)

        if category not in categories:

            categories[category] = {
                "sum_rating": 0.0,
                "count": 0,
                "books": []
            }

        categories[category]["sum_rating"] += rating

        categories[category]["count"] += 1

        categories[category]["books"].append(
            (
                title,
                author,
                rating
            )
        )

    except:
        continue


best_category = None
best_avg = -1


for category, data in categories.items():

    avg_rating = (
        data["sum_rating"]
        / data["count"]
    )

    if avg_rating > best_avg:

        best_avg = avg_rating
        best_category = category


if best_category:

    for title, author, rating in categories[
        best_category
    ]["books"]:

        print(
            f"{best_category}\t"
            f"{best_avg:.2f}\t"
            f"{title}\t"
            f"{author}\t"
            f"{rating:.1f}"
        )