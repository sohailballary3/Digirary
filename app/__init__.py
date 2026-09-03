import os
from flask import Flask, render_template


def create_app(test_config=None):
    """Application factory for Digirary.
    Lightweight, modular, and configurable.
    """
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "digirary-dev-secret-key-lightweight-2026"),
        DATABASE=os.path.join(app.instance_path, "digirary.db"),
    )

    if test_config is not None:
        app.config.from_mapping(test_config)

    # Initialize SQLite database
    from app import database
    database.init_app(app)

    # Register Blueprints
    from app import auth, books, borrow, dashboard, admin, routes
    app.register_blueprint(auth.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(borrow.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(routes.bp)

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"), 500

    return app
