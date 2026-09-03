import os
import sqlite3
from flask import current_app, g


def get_db():
    """Connect to the application's configured SQLite database.
    Reuses the connection if already open in current application context.
    Enforces foreign key constraints.
    """
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        # Enable SQLite foreign key constraint checking
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db


def close_db(e=None):
    """Close the database connection if open."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app=None):
    """Clear existing data and initialize new tables with seed records."""
    if app:
        with app.app_context():
            _execute_schema()
    else:
        _execute_schema()


def _execute_schema():
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)

    # Automatically create instance folder and DB if missing or needs upgrade
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = app.config["DATABASE"]
    
    should_init = False
    if not os.path.exists(db_path):
        should_init = True
    else:
        # Check if new tables (users, borrowings) exist
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cur.fetchone():
                should_init = True
            conn.close()
        except Exception:
            should_init = True

    if should_init:
        with app.app_context():
            _execute_schema()
