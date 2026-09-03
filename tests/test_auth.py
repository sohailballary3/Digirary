from tests.test_base import BaseTestCase


class TestAuthentication(BaseTestCase):
    """Test user registration, login, logout, password hashing, and access control."""

    def test_initial_state_is_logged_out(self):
        """Verify the website initially opens in a completely logged-out state."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Log In", response.data)
        self.assertIn(b"Register", response.data)
        self.assertNotIn(b"Logout", response.data)

    def test_successful_registration_and_no_auto_login(self):
        """Verify registration succeeds and explicitly DOES NOT automatically log in."""
        res = self.register("alice", "alice@example.com", "password123", "password123")
        self.assertEqual(res.status_code, 200)
        # Should show success message and be on login page
        self.assertIn(b"Account created successfully", res.data)
        self.assertIn(b"Sign In", res.data)
        # Verify user is still logged out
        self.assertNotIn(b"Welcome back, alice", res.data)
        self.assertNotIn(b"Logout", res.data)

    def test_duplicate_username_prevented(self):
        """Verify system prevents duplicate usernames."""
        self.register("alice", "alice@example.com", "password123", "password123")
        res = self.register("alice", "another@example.com", "password123", "password123")
        self.assertIn(b"already taken", res.data)

    def test_duplicate_email_prevented(self):
        """Verify system prevents duplicate email addresses."""
        self.register("alice", "alice@example.com", "password123", "password123")
        res = self.register("bob", "alice@example.com", "password123", "password123")
        self.assertIn(b"already registered", res.data)

    def test_password_mismatch_prevented(self):
        """Verify registration rejects mismatched confirmation passwords."""
        res = self.register("charlie", "charlie@example.com", "password123", "different123")
        self.assertIn(b"Passwords do not match", res.data)

    def test_short_password_prevented(self):
        """Verify registration requires at least 6 characters."""
        res = self.register("dave", "dave@example.com", "123", "123")
        self.assertIn(b"Password must be at least 6 characters", res.data)

    def test_login_with_username_and_logout(self):
        """Verify login via username, session establishment, and logout."""
        self.register("elena", "elena@example.com", "secret123", "secret123")
        login_res = self.login("elena", "secret123")
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Welcome back, elena", login_res.data)
        self.assertIn(b"Logout", login_res.data)

        # Now logout
        logout_res = self.logout()
        self.assertEqual(logout_res.status_code, 200)
        self.assertIn(b"successfully logged out", logout_res.data)
        self.assertIn(b"Log In", logout_res.data)

    def test_login_with_email(self):
        """Verify users can log in using their email address."""
        self.register("frank", "frank@example.com", "secret123", "secret123")
        res = self.login("frank@example.com", "secret123")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome back, frank", res.data)

    def test_login_invalid_credentials(self):
        """Verify login rejects invalid password and nonexistent user."""
        res1 = self.login("nonexistent", "badpass")
        self.assertIn(b"Invalid username/email or password", res1.data)

        self.register("grace", "grace@example.com", "password123", "password123")
        res2 = self.login("grace", "wrongpassword")
        self.assertIn(b"Invalid username/email or password", res2.data)

    def test_protected_page_redirects_unauthenticated_user(self):
        """Verify protected routes redirect anonymous visitors to login."""
        res = self.client.get("/dashboard/", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Please log in to access this page", res.data)
        self.assertIn(b"Welcome Back", res.data)
