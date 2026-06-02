"""Book CRUD routes."""

from __future__ import annotations

import math
from typing import Any

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for


book_blueprint = Blueprint("books", __name__)


def mysql():
    return current_app.extensions["mysql_service"]


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


@book_blueprint.get("/")
@book_blueprint.get("/books")
def index():
    filters = {key: request.args.get(key, "") for key in ("q", "source", "category", "author", "publisher", "min_price", "max_price")}
    page = max(1, request.args.get("page", default=1, type=int))
    books, total = mysql().list_books(filters, page)
    edit_source = request.args.get("edit_source", "")
    edit_id = request.args.get("edit_id", "")
    edit_book = mysql().get_book(edit_source, edit_id) if edit_source and edit_id else None
    return render_template(
        "books.html",
        books=books,
        filters=filters,
        page=page,
        pages=max(1, math.ceil(total / 30)),
        total=total,
        edit_book=edit_book,
    )


@book_blueprint.post("/books/save")
def save():
    data = book_form()
    if not data["book_id"] or not data["title"] or data["source"] not in {"tiki", "fahasa"}:
        flash("book_id, source and title are required.", "danger")
    else:
        mysql().save_book(data)
        flash("Book saved.", "success")
    return redirect(url_for("books.index"))


@book_blueprint.post("/books/delete/<source>/<book_id>")
def delete(source: str, book_id: str):
    mysql().delete_book(source, book_id)
    flash("Book deleted.", "success")
    return redirect(url_for("books.index"))
