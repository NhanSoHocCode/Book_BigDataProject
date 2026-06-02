"""Build simple Chart.js payloads from analytics rows."""

from __future__ import annotations

from typing import Any


def columns(rows: list[dict[str, Any]]) -> list[str]:
    found: list[str] = []
    for row in rows:
        for key in row:
            if key not in found:
                found.append(key)
    return found


def chart_payload(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    keys = columns(rows)
    numeric_keys = [
        key for key in keys
        if any(isinstance(row.get(key), (int, float)) for row in rows)
    ]
    if not numeric_keys:
        return None
    label_key = next((key for key in keys if key not in numeric_keys), keys[0])
    value_key = numeric_keys[-1]
    limited = rows[:30]
    return {
        "labels": [str(row.get(label_key, "")) for row in limited],
        "datasets": [{
            "label": value_key,
            "data": [row.get(value_key, 0) for row in limited],
            "backgroundColor": "rgba(13, 110, 253, 0.55)",
            "borderColor": "rgb(13, 110, 253)",
            "borderWidth": 1,
        }],
    }
