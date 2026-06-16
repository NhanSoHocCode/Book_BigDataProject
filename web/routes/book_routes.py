from __future__ import annotations

import math
from datetime import datetime
from typing import Any

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for

from services.book_validation import validate_book
from services.chart_service import columns


book_blueprint = Blueprint("books", __name__)


def query_service():
    return current_app.extensions["book_query_service"]


def crud_service():
    return current_app.extensions["book_crud_service"]


def pagination_window(current: int, total: int) -> list[int | None]:
    if total <= 7:
        return list(range(1, total + 1))
    pages = {1, total, current - 2, current - 1, current, current + 1, current + 2}
    visible = sorted(page for page in pages if 1 <= page <= total)
    result: list[int | None] = []
    for page in visible:
        if result and page - int(result[-1]) > 1:
            result.append(None)
        result.append(page)
    return result


def book_form() -> dict[str, Any]:
    numeric_defaults = {
        "price": "0",
        "original_price": "0",
        "discount_rate": "0",
        "rating": "0",
        "review_count": "0",
        "sold_count": "0",
    }
    data: dict[str, Any] = {}
    for name in (
        "book_id", "source", "title", "author", "publisher", "language_group",
        "main_category", "sub_category", "url",
    ):
        data[name] = request.form.get(name, "").strip()
    for name, default in numeric_defaults.items():
        data[name] = request.form.get(name, "").strip() or default
    for name in ("publish_year", "page_count"):
        data[name] = request.form.get(name, "").strip() or None
    return data


@book_blueprint.get("/books")
def index():
    filters = {
        key: request.args.get(key, "")
        for key in (
            "q", "source", "category", "sub_category", "author", "publisher",
            "min_price", "max_price",
        )
    }
    page = max(1, request.args.get("page", default=1, type=int))
    page_size = 15
    error = None
    try:
        books, total = query_service().list_books(filters, page, page_size)
        category_tree = query_service().book_category_tree()
    except Exception as caught:
        books, total, category_tree = [], 0, {}
        error = f"Không thể đọc dữ liệu sách: {caught}"
    total_pages = max(1, math.ceil(total / page_size))
    if page > total_pages:
        page = total_pages
        try:
            books, total = query_service().list_books(filters, page, page_size)
        except Exception as caught:
            books, total = [], 0
            error = f"Không thể đọc dữ liệu sách: {caught}"
    return render_template(
        "books.html",
        books=books,
        filters=filters,
        page=page,
        pages=total_pages,
        page_size=page_size,
        row_offset=(page - 1) * page_size,
        total=total,
        pagination_items=pagination_window(page, total_pages),
        max_publish_year=datetime.now().year + 1,
        categories=list(category_tree),
        category_tree=category_tree,
        error=error,
    )


@book_blueprint.post("/books/save")
def save():
    data, errors = validate_book(book_form())
    if errors:
        flash("Dữ liệu sách chưa hợp lệ. Vui lòng kiểm tra lại.", "danger")
    else:
        try:
            crud_service().save_book(data)
            flash("Đã lưu sách thành công.", "success")
        except Exception as error:
            flash(f"Không thể lưu sách: {error}", "danger")
    return redirect(url_for("books.index"))


@book_blueprint.post("/books/delete/<source>/<book_id>")
def delete(source: str, book_id: str):
    if request.form.get("confirm") != "true":
        flash("Bạn phải xác nhận trước khi xóa.", "danger")
        return redirect(url_for("books.index"))
    try:
        crud_service().delete_book(source, book_id)
        flash("Đã xóa sách thành công.", "success")
    except Exception as error:
        flash(f"Không thể xóa sách: {error}", "danger")
    return redirect(url_for("books.index"))


@book_blueprint.get("/api/books/<source>/<book_id>")
def api_get_book(source: str, book_id: str):
    try:
        book = query_service().get_book(source, book_id)
    except Exception as error:
        return jsonify({"message": f"Không thể truy vấn Phoenix: {error}"}), 503
    if not book:
        return jsonify({"message": "Không tìm thấy sách."}), 404
    return jsonify({"book": book})


@book_blueprint.post("/api/books")
def api_save_book():
    payload = request.get_json(silent=True) or {}
    data, errors = validate_book(payload)
    operation = payload.get("_operation", "create")
    original_source = str(payload.get("_original_source", "")).strip()
    original_book_id = str(payload.get("_original_book_id", "")).strip()

    if operation not in {"create", "update"}:
        errors["_operation"] = "Thao tác lưu không hợp lệ."
    try:
        if operation == "create" and crud_service().exists(data["source"], data["book_id"]):
            errors["book_id"] = "Book ID này đã tồn tại trong nguồn đã chọn."
        elif operation == "update":
            if not crud_service().exists(original_source, original_book_id):
                return jsonify({"message": "Không tìm thấy sách cần cập nhật."}), 404
            if data["source"] != original_source or data["book_id"] != original_book_id:
                errors["book_id"] = "Không được thay đổi Book ID hoặc nguồn khi cập nhật."
    except Exception as error:
        return jsonify({"message": f"Không thể kiểm tra RowKey qua HappyBase: {error}"}), 503

    if errors:
        return jsonify({
            "message": "Dữ liệu sách chưa hợp lệ.",
            "errors": errors,
        }), 400
    try:
        crud_service().save_book(data)
    except Exception as error:
        return jsonify({"message": f"Không thể lưu dữ liệu vào HBase qua HappyBase: {error}"}), 503
    return jsonify({
        "message": "Đã lưu sách thành công.",
        "book": data,
    })


@book_blueprint.delete("/api/books/<source>/<book_id>")
def api_delete_book(source: str, book_id: str):
    payload = request.get_json(silent=True) or {}
    if payload.get("confirm") is not True:
        return jsonify({"message": "Bạn phải xác nhận trước khi xóa."}), 400
    try:
        if not crud_service().exists(source, book_id):
            return jsonify({"message": "Không tìm thấy sách."}), 404
        crud_service().delete_book(source, book_id)
    except Exception as error:
        return jsonify({"message": f"Không thể xóa dữ liệu HBase qua HappyBase: {error}"}), 503
    return jsonify({"message": "Đã xóa sách thành công."})


@book_blueprint.route("/sql", methods=["GET", "POST"])
def sql_query():
    sql = request.form.get(
        "sql",
        f"SELECT * FROM {current_app.config['PHOENIX_BOOKS_VIEW']} LIMIT 20",
    )
    rows = []
    error = None
    if request.method == "POST":
        rows, error = query_service().phoenix_query(sql)
    return render_template(
        "sql_query.html",
        sql=sql,
        rows=rows,
        columns=columns(rows),
        error=error,
    )