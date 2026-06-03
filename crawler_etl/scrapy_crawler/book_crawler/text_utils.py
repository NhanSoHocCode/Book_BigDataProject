from __future__ import annotations

import re
import unicodedata
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def compact_text(value: Any) -> str | None:
    return " ".join(str(value).split()) if value is not None else None


def clean_title(value: str | None) -> str | None:
    text = compact_text(value)
    if not text:
        return None
    text = re.sub(r"\s*[-|]\s*FAHASA\.COM\s*$", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*FAHASA\.COM\s*$", "", text, flags=re.IGNORECASE)
    return compact_text(text)


def fold_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    folded = "".join(character for character in normalized if not unicodedata.combining(character))
    return folded.replace("đ", "d").replace("Đ", "D").lower()


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d[\d.,]*", str(value))
    if not match:
        return None
    text = match.group(0)
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    else:
        text = text.replace(",", "").replace(".", "")
    try:
        return float(text)
    except ValueError:
        return None


def parse_discount(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:[.,]\d+)?\s*%", str(value))
    if not match:
        return None
    return parse_number(match.group(0))


def parse_decimal(value: Any) -> float | None:
    if value is None:
        return None
    match = re.search(r"-?\d+(?:[.,]\d+)?", str(value))
    if not match:
        return None
    text = match.group(0).replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return None


def parse_human_count(value: Any) -> int | None:
    if value is None:
        return None
    text = fold_text(str(value))
    text = text.replace("da ban", "").replace("luot danh gia", "").strip()
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*([km])?", text)
    if not match:
        return None
    number = float(match.group(1).replace(",", "."))
    suffix = match.group(2)
    if suffix == "k":
        number *= 1_000
    elif suffix == "m":
        number *= 1_000_000
    return int(round(number))


def canonical_url(url: str) -> str:
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def find_metadata(metadata: dict[str, str], *labels: str) -> str | None:
    for key, value in metadata.items():
        if any(label in key for label in labels):
            return value
    return None


def config_main_category(category: dict[str, Any]) -> str | None:
    return category.get("main_category") or category.get("name")


def config_sub_category(category: dict[str, Any]) -> str | None:
    return category.get("sub_category") or category.get("name")
