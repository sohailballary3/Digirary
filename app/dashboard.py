from datetime import date, datetime
from flask import Blueprint, g, render_template
from app.auth import login_required
from app.database import get_db

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@bp.route("/")
@login_required
def index():
    """Display user dashboard with active borrowings, overdue indicators, and borrowing history."""
    db = get_db()
    today = date.today()

    # Active borrowings
    active_rows = db.execute(
        """
        SELECT bw.id as borrowing_id, bw.borrow_date, bw.duration_days, bw.due_date, bw.status,
               b.id as book_id, b.title, b.author, b.cover_gradient, b.total_pages,
               c.name as category_name
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        JOIN categories c ON b.category_id = c.id
        WHERE bw.user_id = ? AND bw.status = 'active'
        ORDER BY bw.due_date ASC
        """,
        (g.user["id"],),
    ).fetchall()

    active_borrowings = []
    for row in active_rows:
        due = row["due_date"]
        # Handle string or date type from SQLite
        if isinstance(due, str):
            due_date_obj = datetime.strptime(due, "%Y-%m-%d").date()
        else:
            due_date_obj = due

        is_overdue = due_date_obj < today
        days_remaining = (due_date_obj - today).days

        active_borrowings.append({
            "borrowing_id": row["borrowing_id"],
            "book_id": row["book_id"],
            "title": row["title"],
            "author": row["author"],
            "category_name": row["category_name"],
            "cover_gradient": row["cover_gradient"],
            "total_pages": row["total_pages"],
            "borrow_date": row["borrow_date"],
            "duration_days": row["duration_days"],
            "due_date": due_date_obj,
            "is_overdue": is_overdue,
            "days_remaining": days_remaining,
        })

    # Borrowing history (returned)
    history_rows = db.execute(
        """
        SELECT bw.id as borrowing_id, bw.borrow_date, bw.duration_days, bw.due_date, bw.return_date, bw.status,
               b.id as book_id, b.title, b.author, b.cover_gradient,
               c.name as category_name
        FROM borrowings bw
        JOIN books b ON bw.book_id = b.id
        JOIN categories c ON b.category_id = c.id
        WHERE bw.user_id = ? AND bw.status = 'returned'
        ORDER BY bw.return_date DESC
        """,
        (g.user["id"],),
    ).fetchall()

    stats = {
        "active_count": len(active_borrowings),
        "overdue_count": sum(1 for b in active_borrowings if b["is_overdue"]),
        "history_count": len(history_rows),
    }

    return render_template(
        "dashboard/index.html",
        active_borrowings=active_borrowings,
        history=history_rows,
        stats=stats,
        today=today,
    )
