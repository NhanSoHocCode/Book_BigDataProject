#!/usr/bin/env python3

import sys

current_key = None
sum_value = 0.0
count = 0

for line in sys.stdin:
    key, value, cnt = line.strip().split("\t")

    value = float(value)
    cnt = int(cnt)

    if current_key == key:
        sum_value += value
        count += cnt
    else:
        if current_key:

            print(
                f"{current_key}\t{sum_value}\t{count}"
            )

        current_key = key
        sum_value = value
        count = cnt

if current_key:
    print(
        f"{current_key}\t{sum_value}\t{count}"
    )
