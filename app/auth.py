import functools
import re
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.database import get_db

bp = Blueprint("auth", __name__)


def login_required(view):
    """Decorator to require user authentication before accessing a view."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        return view(**kwargs)
    return wrapped_view


def admin_required(view):
    """Decorator to require administrator privileges before accessing a view."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("Administrator login required.", "warning")
            return redirect(url_for("auth.login", next=request.url))
        if not g.user["is_admin"]:
            flash("Unauthorized access. Administrator privileges required.", "danger")
            return redirect(url_for("main.index"))
        return view(**kwargs)
    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """Load the current user into Flask's `g` context on each request.
    Strictly depends on an active session. If no session, g.user remains None.
    """
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT id, username, email, is_admin, created_at FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        # If user was deleted or invalid, clear session
        if g.user is None:
            session.clear()


@bp.app_context_processor
def inject_user():
    """Make current_user accessible inside all Jinja templates."""
    return dict(current_user=g.user)


@bp.route("/register", methods=("GET", "POST"))
def register():
    """Handle new user registration.
    NOTE: Users are NEVER automatically logged in upon registration.
    """
    # If user is already logged in, redirect to dashboard
    if g.user is not None:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        error = None

        if not username:
            error = "Username is required."
        elif len(username) < 3 or len(username) > 30:
            error = "Username must be between 3 and 30 characters."
        elif not re.match(r"^[a-zA-Z0-9_]+$", username):
            error = "Username may only contain letters, numbers, and underscores."
        elif not email:
            error = "Email address is required."
        elif not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            error = "Please enter a valid email address."
        elif not password:
            error = "Password is required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        elif password != confirm_password:
            error = "Passwords do not match."

        if error is None:
            db = get_db()
            # Check for duplicate username or email
            existing_user = db.execute(
                "SELECT id, username, email FROM users WHERE username = ? OR email = ?",
                (username, email)
            ).fetchone()

            if existing_user:
                if existing_user["username"].lower() == username.lower():
                    error = f"Username '{username}' is already taken."
                else:
                    error = f"Email '{email}' is already registered."
            else:
                hashed_pw = generate_password_hash(password)
                db.execute(
                    "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, 0)",
                    (username, email, hashed_pw)
                )
                db.commit()

                # User is NOT automatically logged in
                flash("Account created successfully! Please log in with your credentials.", "success")
                return redirect(url_for("auth.login"))

        flash(error, "danger")

    return render_template("auth/register.html")


@bp.route("/login", methods=("GET", "POST"))
def login():
    """Handle user login.
    Accepts either username or email and password.
    """
    # If user is already logged in, redirect to dashboard
    if g.user is not None:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        remember = request.form.get("remember")

        error = None

        if not identifier:
            error = "Please enter your username or email."
        elif not password:
            error = "Please enter your password."

        if error is None:
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = ? OR email = ?",
                (identifier, identifier.lower())
            ).fetchone()

            if user is None or not check_password_hash(user["password_hash"], password):
                error = "Invalid username/email or password."
            else:
                # Login verified - start session
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["is_admin"] = bool(user["is_admin"])
                if remember:
                    session.permanent = True

                flash(f"Welcome back, {user['username']}!", "success")

                # Handle redirect to original page if requested
                next_page = request.args.get("next")
                if next_page and next_page.startswith("/"):
                    return redirect(next_page)
                
                if user["is_admin"]:
                    return redirect(url_for("admin.index"))
                return redirect(url_for("dashboard.index"))

        flash(error, "danger")

    return render_template("auth/login.html")


@bp.route("/logout")
def logout():
    """Clear session and log out the user."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("main.index"))
