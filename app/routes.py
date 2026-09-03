from flask import Blueprint, render_template, request, jsonify
from app.database import get_db

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Render the Digirary home page with live statistics and book collection."""
    db = get_db()

    # Fetch library statistics
    stats = {
        "total_books": db.execute("SELECT COUNT(*) FROM books").fetchone()[0],
        "categories_count": db.execute("SELECT COUNT(*) FROM categories").fetchone()[0],
        "featured_count": db.execute("SELECT COUNT(*) FROM books WHERE featured = 1").fetchone()[0],
        "total_pages": db.execute("SELECT COALESCE(SUM(total_pages), 0) FROM books").fetchone()[0],
        "active_loans": db.execute("SELECT COUNT(*) FROM borrowings WHERE status = 'active'").fetchone()[0],
    }

    # Fetch all categories
    categories = db.execute(
        "SELECT id, name, slug, icon FROM categories ORDER BY name ASC"
    ).fetchall()

    # Fetch initial featured & recent books
    books = db.execute(
        """
        SELECT b.id, b.title, b.author, b.isbn, b.published_year, b.summary,
               b.cover_gradient, b.total_pages, b.rating, b.available, b.featured,
               c.name as category_name, c.slug as category_slug
        FROM books b
        JOIN categories c ON b.category_id = c.id
        ORDER BY b.featured DESC, b.id ASC
        """
    ).fetchall()

    return render_template("index.html", stats=stats, categories=categories, books=books)


@bp.route("/api/books")
def api_books():
    """API endpoint to filter and search books dynamically."""
    query = request.args.get("search", "").strip()
    category_slug = request.args.get("category", "").strip()

    db = get_db()
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

    sql += " ORDER BY b.featured DESC, b.id ASC"

    rows = db.execute(sql, params).fetchall()

    books_data = [
        {
            "id": row["id"],
            "title": row["title"],
            "author": row["author"],
            "isbn": row["isbn"],
            "published_year": row["published_year"],
            "summary": row["summary"],
            "cover_gradient": row["cover_gradient"],
            "total_pages": row["total_pages"],
            "rating": row["rating"],
            "available": bool(row["available"]),
            "featured": bool(row["featured"]),
            "category_name": row["category_name"],
            "category_slug": row["category_slug"],
        }
        for row in rows
    ]

    return jsonify({"success": True, "count": len(books_data), "books": books_data})


@bp.route("/api/books/<int:book_id>")
def api_book_detail(book_id):
    """API endpoint to get full details for a single book."""
    db = get_db()
    row = db.execute(
        """
        SELECT b.*, c.name as category_name, c.slug as category_slug
        FROM books b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
        """,
        (book_id,),
    ).fetchone()

    if row is None:
        return jsonify({"success": False, "error": "Book not found"}), 404

    book = {
        "id": row["id"],
        "title": row["title"],
        "author": row["author"],
        "isbn": row["isbn"],
        "published_year": row["published_year"],
        "summary": row["summary"],
        "cover_gradient": row["cover_gradient"],
        "total_pages": row["total_pages"],
        "rating": row["rating"],
        "available": bool(row["available"]),
        "featured": bool(row["featured"]),
        "category_name": row["category_name"],
        "category_slug": row["category_slug"],
    }
    return jsonify({"success": True, "book": book})
