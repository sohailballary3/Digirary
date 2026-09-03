from datetime import date, datetime
from flask import (
    Blueprint, flash, redirect, render_template, request, url_for
)
from app.auth import admin_required
from app.database import get_db

bp = Blueprint("admin", __name__, url_prefix="/admin")

GRADIENT_PRESETS = [
    ("Indigo Glow", "linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)"),
    ("Ocean Blue", "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)"),
    ("Sky Blue", "linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%)"),
    ("Purple Twilight", "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)"),
    ("Emerald Forest", "linear-gradient(135deg, #10b981 0%, #047857 100%)"),
    ("Golden Amber", "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"),
    ("Rose Sunset", "linear-gradient(135deg, #ec4899 0%, #be185d 100%)"),
    ("Dark Slate", "linear-gradient(135deg, #64748b 0%, #334155 100%)"),
    ("Teal Mint", "linear-gradient(135deg, #14b8a6 0%, #0f766e 100%)"),
]


@bp.route("/")
@admin_required
def index():
    """Admin dashboard overview with key metrics and quick management links."""
    db = get_db()
    today = date.today()

    total_books = db.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    active_loans = db.execute("SELECT COUNT(*) FROM borrowings WHERE status = 'active'").fetchone()[0]

    # Calculate overdue loans
    overdue_loans = db.execute(
        "SELECT COUNT(*) FROM borrowings WHERE status = 'active' AND due_date < ?",
        (today,),
    ).fetchone()[0]

    recent_borrowings = db.execute(
        """
        SELECT bw.*, u.username, b.title
        FROM borrowings bw
        JOIN users u ON bw.user_id = u.id
        JOIN books b ON bw.book_id = b.id
        ORDER BY bw.created_at DESC
        LIMIT 5
        """
    ).fetchall()

    return render_template(
        "admin/index.html",
        total_books=total_books,
        total_users=total_users,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        recent_borrowings=recent_borrowings,
        today=today,
    )


@bp.route("/books")
@admin_required
def books_list():
    """List all books in the catalog with admin editing tools."""
    db = get_db()
    books = db.execute(
        """
        SELECT b.*, c.name as category_name
        FROM books b
        JOIN categories c ON b.category_id = c.id
        ORDER BY b.id DESC
        """
    ).fetchall()
    return render_template("admin/books_list.html", books=books)


@bp.route("/books/add", methods=("GET", "POST"))
@admin_required
def book_add():
    """Add a new book to the catalogue."""
    db = get_db()
    categories = db.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category_id = request.form.get("category_id")
        isbn = request.form.get("isbn", "").strip()
        published_year = request.form.get("published_year", "").strip()
        total_pages = request.form.get("total_pages", "300").strip()
        rating = request.form.get("rating", "4.5").strip()
        summary = request.form.get("summary", "").strip()
        cover_gradient = request.form.get("cover_gradient", GRADIENT_PRESETS[0][1])
        featured = 1 if request.form.get("featured") else 0

        error = None
        if not title:
            error = "Book title is required."
        elif not author:
            error = "Author name is required."
        elif not category_id:
            error = "Category selection is required."

        if error is None:
            try:
                db.execute(
                    """
                    INSERT INTO books (
                        title, author, category_id, isbn, published_year,
                        total_pages, rating, summary, cover_gradient, available, featured
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """,
                    (
                        title,
                        author,
                        category_id,
                        isbn or None,
                        int(published_year) if published_year else None,
                        int(total_pages) if total_pages else 300,
                        float(rating) if rating else 4.5,
                        summary or None,
                        cover_gradient,
                        featured,
                    ),
                )
                db.commit()
                flash(f"Book '{title}' added successfully!", "success")
                return redirect(url_for("admin.books_list"))
            except Exception as e:
                db.rollback()
                error = f"Failed to add book: {e}"

        flash(error, "danger")

    return render_template(
        "admin/book_form.html",
        action="Add",
        book=None,
        categories=categories,
        gradient_presets=GRADIENT_PRESETS,
    )


@bp.route("/books/<int:book_id>/edit", methods=("GET", "POST"))
@admin_required
def book_edit(book_id):
    """Edit an existing book."""
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        flash("Book not found.", "danger")
        return redirect(url_for("admin.books_list"))

    categories = db.execute("SELECT * FROM categories ORDER BY name ASC").fetchall()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category_id = request.form.get("category_id")
        isbn = request.form.get("isbn", "").strip()
        published_year = request.form.get("published_year", "").strip()
        total_pages = request.form.get("total_pages", "300").strip()
        rating = request.form.get("rating", "4.5").strip()
        summary = request.form.get("summary", "").strip()
        cover_gradient = request.form.get("cover_gradient", book["cover_gradient"])
        available = 1 if request.form.get("available") else 0
        featured = 1 if request.form.get("featured") else 0

        error = None
        if not title:
            error = "Book title is required."
        elif not author:
            error = "Author name is required."
        elif not category_id:
            error = "Category selection is required."

        if error is None:
            try:
                db.execute(
                    """
                    UPDATE books SET
                        title = ?, author = ?, category_id = ?, isbn = ?,
                        published_year = ?, total_pages = ?, rating = ?,
                        summary = ?, cover_gradient = ?, available = ?, featured = ?
                    WHERE id = ?
                    """,
                    (
                        title,
                        author,
                        category_id,
                        isbn or None,
                        int(published_year) if published_year else None,
                        int(total_pages) if total_pages else 300,
                        float(rating) if rating else 4.5,
                        summary or None,
                        cover_gradient,
                        available,
                        featured,
                        book_id,
                    ),
                )
                db.commit()
                flash(f"Book '{title}' updated successfully!", "success")
                return redirect(url_for("admin.books_list"))
            except Exception as e:
                db.rollback()
                error = f"Failed to update book: {e}"

        flash(error, "danger")

    return render_template(
        "admin/book_form.html",
        action="Edit",
        book=book,
        categories=categories,
        gradient_presets=GRADIENT_PRESETS,
    )


@bp.route("/books/<int:book_id>/delete", methods=("POST",))
@admin_required
def book_delete(book_id):
    """Delete a book, checking first for active borrowings."""
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        flash("Book not found.", "danger")
        return redirect(url_for("admin.books_list"))

    # Check for active borrowings
    active_loan = db.execute(
        "SELECT id FROM borrowings WHERE book_id = ? AND status = 'active'",
        (book_id,),
    ).fetchone()

    if active_loan:
        flash(f"Cannot delete '{book['title']}' because it is currently borrowed by a user.", "danger")
        return redirect(url_for("admin.books_list"))

    try:
        db.execute("DELETE FROM books WHERE id = ?", (book_id,))
        db.commit()
        flash(f"Book '{book['title']}' deleted successfully.", "success")
    except Exception as e:
        db.rollback()
        flash(f"Error deleting book: {e}", "danger")

    return redirect(url_for("admin.books_list"))


@bp.route("/users")
@admin_required
def users_list():
    """View all registered users and their loan statistics."""
    db = get_db()
    users = db.execute(
        """
        SELECT u.id, u.username, u.email, u.is_admin, u.created_at,
               (SELECT COUNT(*) FROM borrowings WHERE user_id = u.id AND status = 'active') as active_loans_count,
               (SELECT COUNT(*) FROM borrowings WHERE user_id = u.id) as total_loans_count
        FROM users u
        ORDER BY u.id ASC
        """
    ).fetchall()
    return render_template("admin/users.html", users=users)


@bp.route("/borrowings")
@admin_required
def borrowings():
    """View system-wide borrowing history and active loans."""
    db = get_db()
    today = date.today()

    rows = db.execute(
        """
        SELECT bw.*, u.username, u.email, b.title, b.author
        FROM borrowings bw
        JOIN users u ON bw.user_id = u.id
        JOIN books b ON bw.book_id = b.id
        ORDER BY bw.status ASC, bw.due_date ASC
        """
    ).fetchall()

    borrowing_list = []
    for r in rows:
        due = r["due_date"]
        if isinstance(due, str):
            due_date_obj = datetime.strptime(due, "%Y-%m-%d").date()
        else:
            due_date_obj = due

        is_overdue = (r["status"] == "active") and (due_date_obj < today)

        borrowing_list.append({
            "id": r["id"],
            "username": r["username"],
            "email": r["email"],
            "book_title": r["title"],
            "book_author": r["author"],
            "borrow_date": r["borrow_date"],
            "duration_days": r["duration_days"],
            "due_date": due_date_obj,
            "return_date": r["return_date"],
            "status": r["status"],
            "is_overdue": is_overdue,
        })

    return render_template("admin/borrowings.html", borrowings=borrowing_list, today=today)
