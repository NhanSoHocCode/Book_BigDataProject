from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlparse


TEXT_FIELDS = (
    "book_id",
    "source",
    "title",
    "author",
    "publisher",
    "language_group",
    "main_category",
    "sub_category",
    "url",
)

NUMBER_RULES = {
    "price": {"minimum": 0.01, "maximum": None, "integer": False, "label": "Giá bán"},
    "original_price": {"minimum": 0, "maximum": None, "integer": False, "label": "Giá gốc"},
    "discount_rate": {"minimum": 0, "maximum": 100, "integer": False, "label": "Tỷ lệ giảm giá"},
    "rating": {"minimum": 0, "maximum": 5, "integer": False, "label": "Rating"},
    "review_count": {"minimum": 0, "maximum": None, "integer": True, "label": "Số lượt đánh giá"},
    "sold_count": {"minimum": 0, "maximum": None, "integer": True, "label": "Số lượng đã bán"},
    "publish_year": {
        "minimum": 1000,
        "maximum": datetime.now().year + 1,
        "integer": True,
        "label": "Năm xuất bản",
        "optional": True,
    },
    "page_count": {
        "minimum": 1,
        "maximum": None,
        "integer": True,
        "label": "Số trang",
        "optional": True,
    },
}

def validate_book(payload: dict[str, Any]) -> tuple[dict[str, Any], dict[str, str]]:
    data = {
        field: str(payload.get(field, "") or "").strip()
        for field in TEXT_FIELDS
    }
    errors: dict[str, str] = {}
    data["source"] = data["source"].casefold()

    for field, label in (
        ("book_id", "Book ID"),
        ("source", "Nguồn"),
        ("title", "Tên sách"),
        ("url", "URL"),
    ):
        if not data[field]:
            errors[field] = f"{label} không được để trống."

    if data["source"] and data["source"] not in {"tiki", "fahasa"}:
        errors["source"] = "Nguồn chỉ được là tiki hoặc fahasa."

    if len(data["book_id"]) > 150:
        errors["book_id"] = "Book ID không được dài quá 150 ký tự."
    if len(data["title"]) > 500:
        errors["title"] = "Tên sách không được dài quá 500 ký tự."

    if data["url"]:
        parsed_url = urlparse(data["url"])
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            errors["url"] = "URL phải bắt đầu bằng http:// hoặc https://."

    for field, rule in NUMBER_RULES.items():
        raw_value = payload.get(field, "")
        if raw_value in ("", None):
            if rule.get("optional"):
                data[field] = None
                continue
            raw_value = 0
        try:
            value = float(raw_value)
        except (TypeError, ValueError):
            errors[field] = f"{rule['label']} phải là số hợp lệ."
            continue

        if rule["integer"] and not value.is_integer():
            errors[field] = f"{rule['label']} phải là số nguyên."
            continue
        if rule["minimum"] is not None and value < rule["minimum"]:
            errors[field] = f"{rule['label']} phải từ {rule['minimum']} trở lên."
            continue
        if rule["maximum"] is not None and value > rule["maximum"]:
            errors[field] = f"{rule['label']} không được vượt quá {rule['maximum']}."
            continue
        data[field] = int(value) if rule["integer"] else value

    price = data.get("price")
    original_price = data.get("original_price")
    is_price_error = False
    if (
        isinstance(price, (int, float))
        and isinstance(original_price, (int, float))
        and original_price > 0
        and price > original_price
    ):
        last_field = payload.get("_last_focused_field", "")
        is_price_error = True

        if last_field == "original_price":
            errors["original_price"] = "Giá gốc phải lớn hơn hoặc bằng giá bán hiện tại."
        elif last_field == "price":
            errors["price"] = "Giá bán không được lớn hơn giá gốc."
        else:
            errors["price"] = "Giá bán không được vượt quá giá gốc."

    discount_rate = payload.get("discount_rate", "") 
    if isinstance(price, (int, float)) and isinstance(original_price, (int, float)) and not is_price_error:
        if discount_rate not in ("", None):
            try:
                user_discount = float(discount_rate)
                
                if original_price == 0 or original_price is None:
                    if user_discount > 0:
                        errors["discount_rate"] = "Không thể tính tỷ lệ giảm giá khi chưa có Giá gốc."
                    else:
                        data["discount_rate"] = 0.0

                elif original_price > 0 and price > 0:
                    real_discount = (1 - (price / original_price)) * 100
                    
                    if abs(real_discount - user_discount) > 1:
                        errors["discount_rate"] = f"Tỷ lệ giảm giá không khớp với giá bán và giá gốc (Nên điền khoảng {round(real_discount)}%)."
                    else:
                        data["discount_rate"] = user_discount 
                        
            except (ValueError, TypeError):
                errors["discount_rate"] = "Tỷ lệ giảm giá phải là số hợp lệ."
        else:
            data["discount_rate"] = 0.0 if original_price == 0 else round((1 - (price / original_price)) * 100, 1) if (original_price or 0) > 0 else 0.0

    for field in ("author", "publisher", "language_group", "main_category", "sub_category"):
        data[field] = data[field] or "Unknown"

    return data, errors
