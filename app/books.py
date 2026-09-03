from flask import Blueprint, abort, render_template, request
from app.database import get_db

bp = Blueprint("books", __name__, url_prefix="/books")


@bp.route("/")
def list_books():
    """Browse all books in the catalogue with optional search and category filters."""
    query = request.args.get("q", "").strip()
    category_slug = request.args.get("category", "").strip()

    db = get_db()

    # Get categories for filter chips
    categories = db.execute(
        "SELECT id, name, slug, icon FROM categories ORDER BY name ASC"
    ).fetchall()

    # Construct dynamic query
    sql = """
        SELECT b.id, b.title, b.author, b.isbn, b.published_year, b.summary,
               b.cover_gradient, b.total_pages, b.rating, b.available, b.featured,
               c.name as category_name, c.slug as category_slug
        FROM books b
        JOIN categories c ON b.category_id = c.id
        WHERE 1=1
    """
    params = []

    if query:
        sql += " AND (b.title LIKE ? OR b.author LIKE ? OR b.summary LIKE ?)"
        wildcard = f"%{query}%"
        params.extend([wildcard, wildcard, wildcard])

    if category_slug and category_slug != "all":
        sql += " AND c.slug = ?"
        params.append(category_slug)

    sql += " ORDER BY b.available DESC, b.featured DESC, b.id ASC"

    books = db.execute(sql, params).fetchall()

    return render_template(
        "books/list.html",
        books=books,
        categories=categories,
        current_query=query,
        current_category=category_slug or "all",
    )


@bp.route("/<int:book_id>")
def detail(book_id):
    """Display in-depth information for an individual book."""
    db = get_db()
    book = db.execute(
        """
        SELECT b.*, c.name as category_name, c.slug as category_slug
        FROM books b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
        """,
        (book_id,),
    ).fetchone()

    if book is None:
        abort(404)

    # Check if this book has active borrowings or related recommendations
    related_books = db.execute(
        """
        SELECT b.id, b.title, b.author, b.cover_gradient, b.rating, b.available,
               c.name as category_name, c.slug as category_slug
        FROM books b
        JOIN categories c ON b.category_id = c.id
        WHERE b.category_id = ? AND b.id != ?
        LIMIT 3
        """,
        (book["category_id"], book_id),
    ).fetchall()

    return render_template("books/detail.html", book=book, related_books=related_books)
