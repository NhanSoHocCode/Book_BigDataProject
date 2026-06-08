"""Normalize raw book records from Tiki and Fahasa into one schema."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from datetime import datetime


FIELDS = [
    "book_id",
    "source",
    "title",
    "author",
    "publisher",
    "language_group",
    "main_category",
    "sub_category",
    "price",
    "original_price",
    "discount_rate",
    "rating",
    "review_count",
    "sold_count",
    "publish_year",
    "page_count",
    "url",
]

CATEGORY_MAPPING = {
    # Văn học
    "sach van hoc": "Văn học",
    "fiction literature": "Văn học",
    "van hoc": "Văn học",
    "fiction": "Văn học",

    # Thiếu nhi
    "children s books": "Thiếu nhi",
    "thieu nhi": "Thiếu nhi",
    "sach thieu nhi": "Thiếu nhi",

    # Tâm lý
    "sach tam ly gioi tinh": "Tâm lý - Kỹ năng sống",
    "tam ly ky nang song": "Tâm lý - Kỹ năng sống",
    "personal development": "Tâm lý - Kỹ năng sống",
    "how to self help": "Tâm lý - Kỹ năng sống",
    "mind body spirit": "Tâm lý - Kỹ năng sống",
    "sach ky nang song": "Tâm lý - Kỹ năng sống",

    # Giáo khoa
    "giao khoa tham khao": "Giáo khoa - Tham khảo",
    "education teaching": "Giáo khoa - Tham khảo",
    "education reference": "Giáo khoa - Tham khảo",

    # Ngoại ngữ
    "reference": "Sách học ngoại ngữ",
    "sach hoc ngoai ngu": "Sách học ngoại ngữ",
    "other languages": "Sách học ngoại ngữ",
    
    #Từ điển
    "dictionaries languages": "Từ điển",
    "dictionary": "Từ điển",
    
    # Kinh tế
    "kinh te": "Kinh tế",
    "business finance management": "Kinh tế",
    "business economics": "Kinh tế",
    "sach kinh te": "Kinh tế",

    # Công nghệ thông tin
    "sach cong nghe thong tin": "Công nghệ thông tin",
    "computing": "Công nghệ thông tin",

    # Khoa học - Công nghệ
    "science technology": "Khoa học - Công nghệ",
    "technology engineering": "Khoa học - Công nghệ",
    "science geography": "Khoa học - Công nghệ",

    # Manga - Comic
    "graphic novels anime manga": "Manga - Comic",
    "manga comic": "Manga - Comic",
    "truyen tranh manga comic": "Manga - Comic",

    # Tiểu sử - Hồi ký
    "tieu su hoi ky": "Tiểu sử - Hồi ký",
    "biography": "Tiểu sử - Hồi ký",
    "biographies memoirs": "Tiểu sử - Hồi ký",

    # Tạp chí
    "tap chi catalogue": "Tạp chí",
    "magazines": "Tạp chí",

    # Gia đình - Đời sống
    "sach thuong thuc gia dinh": "Gia đình - Đời sống",
    "crafts and hobbies": "Gia đình - Đời sống",
    "home garden": "Gia đình - Đời sống",
    
    # Y học - Sức khỏe
    "sach y hoc": "Y học - Sức khỏe",
    "health": "Y học - Sức khỏe",
    "medical books": "Y học - Sức khỏe",

    # Văn hóa - Xã hội
    "sach van hoa dia ly du lich": "Văn hóa - Xã hội",
    "history politics social sciences": "Văn hóa - Xã hội",
    "society social sciences": "Văn hóa - Xã hội",

    # Văn hóa - Xã hội mở rộng
    "sach chinh tri phap ly": "Văn hóa - Xã hội",
    "history archaeology": "Văn hóa - Xã hội",
    "sach lich su": "Văn hóa - Xã hội",
    "natural history": "Văn hóa - Xã hội",
    "travel holiday": "Văn hóa - Xã hội",

    # Nông - Lâm - Ngư nghiệp
    "sach nong lam ngu nghiep": "Nông - Lâm - Ngư nghiệp",

    # Nuôi dạy con
    "nuoi day con": "Nuôi dạy con",
    "parenting relationships": "Nuôi dạy con",

    # Ẩm thực
    "cookbooks food wine": "Ẩm thực",
    "food drink": "Ẩm thực",
    
    # Nghệ thuật
    "art photography": "Nghệ thuật - Nhiếp ảnh",

    # Thể thao
    "the duc the thao": "Thể dục Thể thao - Giải trí",
    "humour": "Thể dục Thể thao - Giải trí",
    "entertainment": "Thể dục Thể thao - Giải trí",

    # Văn học mở rộng
    "dam my": "Văn học",
    "science fiction fantasy horror": "Văn học",
    "romance": "Văn học",
    "poetry drama": "Văn học",
    "crime thriller": "Văn học",
}

PUBLISHER_MAPPING = {
    # Nhà Xuất Bản Trẻ
    "nxb tre": "Nhà Xuất Bản Trẻ",
    "tre": "Nhà Xuất Bản Trẻ",

    # Nhà Xuất Bản Thế Giới
    "nha xuat ban the gioi": "Nhà Xuất Bản Thế Giới",
    "the gioi": "Nhà Xuất Bản Thế Giới",
    "nxb the gioi": "Nhà Xuất Bản Thế Giới",

    # Nhà Xuất Bản Dân Trí
    "dan tri": "Nhà Xuất Bản Dân Trí",
    "nha xuat ban dan tri": "Nhà Xuất Bản Dân Trí",
    "nxb dan tri": "Nhà Xuất Bản Dân Trí",
    "dan tri publishing": "Nhà Xuất Bản Dân Trí",

    # Nhà Xuất Bản Kim Đồng
    "kim dong": "Nhà Xuất Bản Kim Đồng",
    "nha xuat ban kim dong": "Nhà Xuất Bản Kim Đồng",
    "nxb kim dong": "Nhà Xuất Bản Kim Đồng",

    # Nhà Xuất Bản Hà Nội
    "nha xuat ban ha noi": "Nhà Xuất Bản Hà Nội",
    "ha noi": "Nhà Xuất Bản Hà Nội",
    "nxb ha noi": "Nhà Xuất Bản Hà Nội",

    # Nhà Xuất Bản Đại Học Quốc Gia Hà Nội
    "dai hoc quoc gia ha noi": "Nhà Xuất Bản Đại Học Quốc Gia Hà Nội",
    "nha xuat ban dai hoc quoc gia ha noi": "Nhà Xuất Bản Đại Học Quốc Gia Hà Nội",
    "nxb dai hoc quoc gia ha noi": "Nhà Xuất Bản Đại Học Quốc Gia Hà Nội",
    "dhqg ha noi": "Nhà Xuất Bản Đại Học Quốc Gia Hà Nội",

    # Nhà Xuất Bản Văn Học
    "van hoc": "Nhà Xuất Bản Văn Học",
    "nha xuat ban van hoc": "Nhà Xuất Bản Văn Học",

    # Nhà Xuất Bản Hồng Đức
    "nha xuat ban hong duc": "Nhà Xuất Bản Hồng Đức",
    "hong duc": "Nhà Xuất Bản Hồng Đức",
    "nxb hong duc": "Nhà Xuất Bản Hồng Đức",
    
    # Nhà Xuất Bản Tổng Hợp TP.HCM
    "nha xuat ban tong hop tp hcm": "Nhà Xuất Bản Tổng Hợp TP.HCM",
    "nxb tong hop tphcm": "Nhà Xuất Bản Tổng Hợp TP.HCM",
    "tong hop thanh pho ho chi minh": "Nhà Xuất Bản Tổng Hợp TP.HCM",
    "tong hop tphcm": "Nhà Xuất Bản Tổng Hợp TP.HCM",
    "tong hop tp hcm": "Nhà Xuất Bản Tổng Hợp TP.HCM",
    "nxb tong hop thanh pho ho chi minh": "Nhà Xuất Bản Tổng Hợp TP.HCM",
    "tong hop ho chi minh": "Nhà Xuất Bản Tổng Hợp TP.HCM",

    # Nhà Xuất Bản Lao Động
    "nha xuat ban lao dong": "Nhà Xuất Bản Lao Động",
    "lao dong": "Nhà Xuất Bản Lao Động",
    "nxb lao dong": "Nhà Xuất Bản Lao Động",

    # Nhà Xuất Bản Công Thương
    "nha xuat ban cong thuong": "Nhà Xuất Bản Công Thương",
    "cong thuong": "Nhà Xuất Bản Công Thương",

    # Nhà Xuất Bản Phụ Nữ Việt Nam
    "nha xuat ban phu nu viet nam": "Nhà Xuất Bản Phụ Nữ Việt Nam",
    "phu nu viet nam": "Nhà Xuất Bản Phụ Nữ Việt Nam",
    "nxb phu nu viet nam": "Nhà Xuất Bản Phụ Nữ Việt Nam",
    "nha xuat ban phu nu": "Nhà Xuất Bản Phụ Nữ Việt Nam",
    "phu nu": "Nhà Xuất Bản Phụ Nữ Việt Nam",
    "nxb phu nu": "Nhà Xuất Bản Phụ Nữ Việt Nam",

    # Nhà Xuất Bản Thanh Niên
    "thanh nien": "Nhà Xuất Bản Thanh Niên",
    "nxb thanh nien": "Nhà Xuất Bản Thanh Niên",
    "nha xuat ban thanh nien": "Nhà Xuất Bản Thanh Niên",

    # HarperCollins
    "harpercollins": "HarperCollins",
    "harper collins": "HarperCollins",
    "harpercollins publishers": "HarperCollins",
    "harper collins publishers": "HarperCollins",
    "harpercollins us": "HarperCollins",
    "harpercollins publishers inc": "HarperCollins",
    "harpercollins publishers ltd": "HarperCollins",
    "harpercollins leadership": "HarperCollins",
    "harpercollinsireland": "HarperCollins",
    "harpercollins s": "HarperCollins",
    "harper collins- usborne": "HarperCollins",
    "harper collins publ. uk": "HarperCollins",

    # Penguin Books
    "penguin books": "Penguin Books",
    "penguin books ltd": "Penguin Books",

    # Nhà Xuất Bản Tri Thức
    "tri thuc": "Nhà Xuất Bản Tri Thức",
    "nha xuat ban tri thuc": "Nhà Xuất Bản Tri Thức",
    
    # Nhà Xuất Bản Hội Nhà Văn
    "hoi nha van": "Nhà Xuất Bản Hội Nhà Văn",

    # Nhà Xuất Bản Đại Học Huế
    "dai hoc hue": "Nhà Xuất Bản Đại Học Huế",

    # Nhà Xuất Bản Đại Học Sư Phạm
    "dai hoc su pham": "Nhà Xuất Bản Đại Học Sư Phạm",
    "nxb dai hoc su pham": "Nhà Xuất Bản Đại Học Sư Phạm",
    "nha xuat ban dai hoc su pham": "Nhà Xuất Bản Đại Học Sư Phạm",

    # Bloomsbury
    "bloomsbury publishing": "Bloomsbury",
    "bloomsbury publishing plc": "Bloomsbury",
    "bloomsbury": "Bloomsbury",
    

    # Cambridge University Press
    "cambridge university": "Cambridge University Press",
    "cambridge university press": "Cambridge University Press",
    "cambridge university press and assessment": "Cambridge University Press",
    "cambridge university press & assessment": "Cambridge University Press",
    "cambridge": "Cambridge University Press",

    # Nhà Xuất Bản Đà Nẵng
    "da nang": "Nhà Xuất Bản Đà Nẵng",
    "nha xuat ban da nang": "Nhà Xuất Bản Đà Nẵng",
    "nxb da nang": "Nhà Xuất Bản Đà Nẵng",

    # Unknown
    "dang cap nhat": "Unknown",
    
    # Nhà Xuất Bản Giáo Dục Việt Nam
    "giao duc viet nam": "Nhà Xuất Bản Giáo Dục Việt Nam",
    "nxb giao duc viet nam": "Nhà Xuất Bản Giáo Dục Việt Nam",
    
    #Nhà Xuất Bản Lao Động Xã Hội
    "nxb lao dong xa hoi": "Nhà Xuất Bản Lao Động Xã Hội",
    "nha xuat ban lao dong xa hoi": "Nhà Xuất Bản Lao Động Xã Hội",
    
    #Nhà Xuất Bản Văn Học
    "nxb van hoc": "Nhà Xuất Bản Văn Học",
    
    #Nhà Xuất Bản Chính Trị Quốc Gia Sự Thật
    "chinh tri quoc gia su that":
    "Nhà Xuất Bản Chính Trị Quốc Gia Sự Thật",
    
    #Nhà Xuất Bản Công Thương
    "nxb cong thuong": "Nhà Xuất Bản Công Thương",
    
    #OEM
    "oem": "OEM",
    
    #Nhà Xuất Bản Văn Hóa - Văn Nghệ
    "nxb van hoa van nghe":
    "Nhà Xuất Bản Văn Hóa - Văn Nghệ",
    "nha xuat ban van hoa van nghe tp hcm":
    "Nhà Xuất Bản Văn Hóa - Văn Nghệ",
    
    #Nhà Xuất Bản Khoa Học Xã Hội
    "khoa hoc xa hoi":
    "Nhà Xuất Bản Khoa Học Xã Hội",
    
    # Nhà Xuất Bản Văn Hoá Thông Tin
    "nxb van hoa thong tin":
    "Nhà Xuất Bản Văn Hoá Thông Tin",
    
        # Nhà Xuất Bản Từ Điển Bách Khoa
    "nha xuat ban tu dien bach khoa":
        "Nhà Xuất Bản Từ Điển Bách Khoa",
    "nxb tu dien bach khoa":
        "Nhà Xuất Bản Từ Điển Bách Khoa",

    # Nhà Xuất Bản Y Học
    "nha xuat ban y hoc":
        "Nhà Xuất Bản Y Học",
    "nxb y hoc":
        "Nhà Xuất Bản Y Học",

    # Nhà Xuất Bản Tài Chính
    "nha xuat ban tai chinh":
        "Nhà Xuất Bản Tài Chính",
    "nxb tai chinh":
        "Nhà Xuất Bản Tài Chính",
    "tai chinh":
        "Nhà Xuất Bản Tài Chính",

    # Nhà Xuất Bản Kinh Tế - Tài Chính
    "nha xuat ban kinh te tai chinh":
        "Nhà Xuất Bản Kinh Tế - Tài Chính",

    # Nhà Xuất Bản Hội Nhà Văn
    "nha xuat ban hoi nha van":
        "Nhà Xuất Bản Hội Nhà Văn",
    "nxb hoi nha van":
        "Nhà Xuất Bản Hội Nhà Văn",
        
    # Nhà Xuất Bản Đại Học Sư Phạm TP.HCM
    "dai hoc su pham thanh pho ho chi minh": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "dai hoc su pham tp hcm": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "dai hoc su pham tphcm": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "dai hoc su pham tp ho chi minh": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "nxb dai hoc su pham tp hcm": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "nxb dai hoc su pham tphcm": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "nha xuat ban dai hoc su pham tphcm": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    "su pham tp hcm": "Nhà Xuất Bản Đại Học Sư Phạm TP.HCM",
    
    #Oxford University Press
    "oxford university press": "Oxford University Press",
    "oxford university press uk": "Oxford University Press",
    
    #Nhà Xuất Bản Thông Tin Và Truyền Thông
    "nha xuat ban thong tin va truyen thong": "Nhà Xuất Bản Thông Tin Và Truyền Thông",
    "thong tin va truyen thong": "Nhà Xuất Bản Thông Tin Và Truyền Thông",
    
    #Nhà Xuất Bản Thể Thao Và Du Lịch
    "nha xuat ban the thao va du lich": "Nhà Xuất Bản Thể Thao Và Du Lịch",
    "the thao va du lich": "Nhà Xuất Bản Thể Thao Và Du Lịch",
    "nxb the thao va du lich": "Nhà Xuất Bản Thể Thao Và Du Lịch",
    
    #Nhà Xuất Bản Thanh Hoá
    "nha xuat ban thanh hoa": "Nhà Xuất Bản Thanh Hoá",
    "thanh hoa": "Nhà Xuất Bản Thanh Hoá",
    
    #Nhà Xuất Bản Hải Phòng
    "nha xuat ban hai phong": "Nhà Xuất Bản Hải Phòng",
    "hai phong": "Nhà Xuất Bản Hải Phòng",
    
    
    #Nhà Xuất Bản Thông Tấn
    "nha xuat ban thong tan": "Nhà Xuất Bản Thông Tấn",
    "thong tan": "Nhà Xuất Bản Thông Tấn",
    
    #Nhà Xuất Bản Đồng Nai
    "nha xuat ban dong nai": "Nhà Xuất Bản Đồng Nai",
    "dong nai": "Nhà Xuất Bản Đồng Nai",
    "nxb dong nai": "Nhà Xuất Bản Đồng Nai",
    
    #Nhà Xuất Bản Mỹ Thuật
    "nha xuat ban my thuat": "Nhà Xuất Bản Mỹ Thuật",
    "my thuat": "Nhà Xuất Bản Mỹ Thuật",
    "nxb my thuat": "Nhà Xuất Bản Mỹ Thuật",
    
    #Nhà Xuất Bản Quân Đội Nhân Dân
    "nha xuat ban quan doi nhan dan": "Nhà Xuất Bản Quân Đội Nhân Dân",
    "quan doi nhan dan": "Nhà Xuất Bản Quân Đội Nhân Dân",
    
    #Nhà Xuất Bản Công An Nhân Dân
    "nha xuat ban cong an nhan dan": "Nhà Xuất Bản Công An Nhân Dân",
    "cong an nhan dan": "Nhà Xuất Bản Công An Nhân Dân",
    
    # Penguin
    "penguin us": "Penguin",
    "penguin group us": "Penguin",
    "penguin group": "Penguin",
    "penguin publishing group": "Penguin",

    # Penguin Books
    "penguin books uk": "Penguin Books",

    # Penguin Random House
    "penguin random house us": "Penguin Random House",
    "penguin random house uk": "Penguin Random House",
    "penguin random house children s uk": "Penguin Random House",
}

LANGUAGE_MAPPING = {
    "vietnamese": "Tiếng Việt",
    "english": "Tiếng Anh",
}


def clean_text(value: Any, default: str | None = None) -> str | None:
    if value is None:
        return default
    text = " ".join(str(value).replace("\x00", "").split())
    return text or default


def fold_key(value: Any) -> str:
    text = clean_text(value, "") or ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(character for character in text if not unicodedata.combining(character))
    text = text.replace("đ", "d").replace("Đ", "D").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def normalize_category(value: Any, default: str = "Unknown") -> str:
    text = clean_text(value, default)
    if not text or text == default:
        return default

    key = fold_key(text)
    return CATEGORY_MAPPING.get(key, text)


def normalize_publisher(value: Any, default: str = "Unknown") -> str:
    text = clean_text(value, default)

    if not text or text == default:
        return default

    key = fold_key(text)
    return PUBLISHER_MAPPING.get(key, text)


def normalize_language(value: Any, default: str = "Unknown") -> str:
    text = clean_text(value, default)

    if not text or text == default:
        return default

    key = fold_key(text)
    return LANGUAGE_MAPPING.get(key, text)


def number(value: Any, default: float | None = None) -> float | None:
    if value in (None, ""):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d[\d.,]*", str(value))
    if not match:
        return default
    text = match.group(0)
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif text.count(".") > 1 or text.count(",") > 1:
        text = text.replace(".", "").replace(",", "")
    elif "," in text:
        text = text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return default


def integer(value: Any, default: int | None = None) -> int | None:
    parsed = number(value)
    return int(parsed) if parsed is not None else default


def tiki_url(value: Any) -> str | None:
    url = clean_text(value)
    if not url:
        return None
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return f"https://tiki.vn/{url.lstrip('/')}"


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    source = clean_text(record.get("source"), "unknown").lower()

    raw_price = number(record.get("price"), 0.0)
    original_price = number(record.get("original_price"), raw_price)

    if original_price is not None and raw_price is not None and original_price < raw_price:
        original_price = raw_price

    discount_rate = number(record.get("discount_rate"))

    if discount_rate is not None:
        discount_rate = abs(discount_rate)

    if discount_rate is None and original_price and raw_price is not None:
        discount_rate = max(0.0, round((original_price - raw_price) * 100 / original_price, 2))

    rating = number(record.get("rating"), 0.0)
    if rating is None or rating < 0 or rating > 5:
        rating = 0.0

    publish_year = integer(record.get("publish_year"))
    current_year = datetime.now().year
    if publish_year is not None and not (1800 <= publish_year <= current_year):
        publish_year = None

    page_count = integer(record.get("page_count"))
    if page_count is not None and page_count <= 0:
        page_count = None

    normalized = {
        "book_id": clean_text(record.get("book_id")),
        "source": source,
        "title": clean_text(record.get("title")),
        "author": normalize_name(record.get("author")),
        "publisher": normalize_publisher(record.get("publisher")),
        "language_group": normalize_language(record.get("language_group")),
        "main_category": normalize_category(record.get("main_category")),
        "sub_category": clean_text(record.get("sub_category"), "Unknown"),
        "price": raw_price,
        "original_price": original_price,
        "discount_rate": discount_rate or 0.0,
        "rating": rating,
        "review_count": integer(record.get("review_count"), 0),
        "sold_count": integer(record.get("sold_count"), 0),
        "publish_year": publish_year,
        "page_count": page_count,
        "url": tiki_url(record.get("url")) if source == "tiki" else clean_text(record.get("url")),
    }

    return {field: normalized[field] for field in FIELDS}


def normalize_file(input_path: Path, output_path: Path) -> list[dict[str, Any]]:
    with input_path.open("r", encoding="utf-8") as file:
        records = json.load(file)
    normalized = [normalize_record(record) for record in records]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        json.dump(normalized, file, ensure_ascii=False, indent=2)
    return normalized

def normalize_name(value: Any, default: str = "Unknown") -> str:
    text = clean_text(value, default)
    if not text or text == default:
        return default

    if text.isupper():
        return text.title()

    return text

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = normalize_file(args.input, args.output)
    print(f"Wrote {len(records)} normalized records to {args.output}")

if __name__ == "__main__":
    main()
