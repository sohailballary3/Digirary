from datetime import date, timedelta
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from app.auth import login_required
from app.database import get_db

bp = Blueprint("borrow", __name__)

ALLOWED_DURATIONS = [7, 14, 30]


@bp.route("/books/<int:book_id>/borrow", methods=("GET", "POST"))
@login_required
def borrow_book(book_id):
    """Allow a logged-in user to borrow an available book, selecting 7, 14, or 30 days."""
    db = get_db()

    book = db.execute(
        """
        SELECT b.*, c.name as category_name
        FROM books b
        JOIN categories c ON b.category_id = c.id
        WHERE b.id = ?
        """,
        (book_id,),
    ).fetchone()

    if book is None:
        flash("The requested book does not exist.", "danger")
        return redirect(url_for("books.list_books"))

    # Prevent duplicate active borrowing of the same book by this user
    existing_borrow = db.execute(
        """
        SELECT id FROM borrowings
        WHERE user_id = ? AND book_id = ? AND status = 'active'
        """,
        (g.user["id"], book_id),
    ).fetchone()

    if existing_borrow:
        flash("You are already borrowing a copy of this book.", "warning")
        return redirect(url_for("dashboard.index"))

    if not book["available"]:
        flash(f"'{book['title']}' is currently borrowed and unavailable.", "warning")
        return redirect(url_for("books.detail", book_id=book_id))

    today = date.today()

    if request.method == "POST":
        try:
            duration_days = int(request.form.get("duration", 14))
        except (ValueError, TypeError):
            duration_days = 14

        if duration_days not in ALLOWED_DURATIONS:
            flash("Invalid borrowing duration selected. Choose 7, 14, or 30 days.", "danger")
            return redirect(url_for("borrow.borrow_book", book_id=book_id))

        due_date = today + timedelta(days=duration_days)

        # Atomic transaction: insert borrowing record and mark book unavailable
        try:
            db.execute(
                """
                INSERT INTO borrowings (user_id, book_id, borrow_date, duration_days, due_date, status)
                VALUES (?, ?, ?, ?, ?, 'active')
                """,
                (g.user["id"], book_id, today.isoformat(), duration_days, due_date.isoformat()),
            )
            db.execute(
                "UPDATE books SET available = 0 WHERE id = ?",
                (book_id,),
            )
            db.commit()

            flash(
                f"Successfully borrowed '{book['title']}'! Due date: {due_date.strftime('%B %d, %Y')} ({duration_days} days).",
                "success",
            )
            return redirect(url_for("dashboard.index"))
        except Exception as e:
            db.rollback()
            flash(f"An error occurred while processing your borrowing request: {e}", "danger")
            return redirect(url_for("books.detail", book_id=book_id))

    # Calculate preview dates for form
    duration_previews = [
        {
            "days": days,
            "due_date": (today + timedelta(days=days)).strftime("%b %d, %Y"),
            "recommended": days == 14,
        }
        for days in ALLOWED_DURATIONS
    ]

    return render_template(
        "books/borrow.html",
        book=book,
        duration_previews=duration_previews,
        today_formatted=today.strftime("%B %d, %Y"),
    )


@bp.route("/borrowings/<int:borrowing_id>/return", methods=("POST",))
@login_required
def return_book(borrowing_id):
    """Process return of a borrowed book by the borrower or an admin."""
    db = get_db()

    borrowing = db.execute(
        """
        SELECT bw.*, b.title, b.id as book_id
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        WHERE bw.id = ?
        """,
        (borrowing_id,),
    ).fetchone()

    if borrowing is None:
        flash("Borrowing record not found.", "danger")
        return redirect(url_for("dashboard.index"))

    # Only borrower or admin can return
    if borrowing["user_id"] != g.user["id"] and not g.user["is_admin"]:
        flash("Unauthorized action. You can only return books you have borrowed.", "danger")
        return redirect(url_for("dashboard.index"))

    if borrowing["status"] == "returned":
        flash("This book has already been returned.", "info")
        return redirect(url_for("dashboard.index"))

    today = date.today()

    try:
        # Atomic return: mark borrowing returned with today's date, make book available
        db.execute(
            """
            UPDATE borrowings
            SET status = 'returned', return_date = ?
            WHERE id = ?
            """,
            (today.isoformat(), borrowing_id),
        )
        db.execute(
            "UPDATE books SET available = 1 WHERE id = ?",
            (borrowing["book_id"],),
        )
        db.commit()

        flash(f"'{borrowing['title']}' has been returned successfully. Thank you!", "success")
    except Exception as e:
        db.rollback()
        flash(f"Failed to process return: {e}", "danger")

    if request.referrer and "admin" in request.referrer and g.user["is_admin"]:
        return redirect(url_for("admin.borrowings"))
    return redirect(url_for("dashboard.index"))
