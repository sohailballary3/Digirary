#!/usr/bin/env python3
"""
Digirary - Digital Library Application
Entry point for running the local development server.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("  * Digirary Digital Library is starting...")
    print("  * Open your browser at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=False)
