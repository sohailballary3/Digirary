import os
import tempfile
import unittest
from app import create_app
from app.database import init_db


class BaseTestCase(unittest.TestCase):
    """Base test fixture setting up an isolated temporary database for each test."""

    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app = create_app({
            "TESTING": True,
            "DATABASE": self.db_path,
            "SECRET_KEY": "test-secret-key-digirary",
            "WTF_CSRF_ENABLED": False,
        })
        self.client = self.app.test_client()

        with self.app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def register(self, username="testuser", email="test@example.com", password="password123", confirm="password123"):
        return self.client.post(
            "/register",
            data={
                "username": username,
                "email": email,
                "password": password,
                "confirm_password": confirm,
            },
            follow_redirects=True,
        )

    def login(self, identifier="testuser", password="password123"):
        return self.client.post(
            "/login",
            data={
                "identifier": identifier,
                "password": password,
            },
            follow_redirects=True,
        )

    def logout(self):
        return self.client.get("/logout", follow_redirects=True)
