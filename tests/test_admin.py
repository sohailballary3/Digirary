from tests.test_base import BaseTestCase


class TestAdminFunctionality(BaseTestCase):
    """Test administrator authorization, book management (CRUD), user directory, and audit logs."""

    def test_anonymous_access_to_admin_denied(self):
        """Verify unauthenticated visitors cannot access admin pages."""
        res = self.client.get("/admin/", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Administrator login required", res.data)
        self.assertIn(b"Welcome Back", res.data)

    def test_normal_user_access_to_admin_denied(self):
        """Verify standard registered members are blocked from admin portal."""
        self.register("standard_reader", "reader@example.com", "password123", "password123")
        self.login("standard_reader", "password123")

        res = self.client.get("/admin/", follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Unauthorized access. Administrator privileges required", res.data)

    def test_admin_login_and_dashboard_access(self):
        """Verify pre-seeded admin user can log in and view dashboard."""
        res = self.login("admin", "admin123")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Admin Dashboard", res.data)
        self.assertIn(b"Total Catalogue Books", res.data)

    def test_admin_add_book(self):
        """Verify admin can add a new book to the catalogue."""
        self.login("admin", "admin123")

        add_res = self.client.post(
            "/admin/books/add",
            data={
                "title": "Structure and Interpretation of Computer Programs",
                "author": "Harold Abelson & Gerald Jay Sussman",
                "category_id": "1",
                "isbn": "978-0262510875",
                "published_year": "1996",
                "total_pages": "657",
                "rating": "4.9",
                "summary": "A foundational computer science text exploring computational abstractions.",
                "cover_gradient": "linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%)",
                "featured": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(add_res.status_code, 200)
        self.assertIn(b"added successfully", add_res.data)

        # Check it appears in public catalog
        catalog_res = self.client.get("/books/?q=Structure")
        self.assertIn(b"Structure and Interpretation", catalog_res.data)

    def test_admin_edit_book(self):
        """Verify admin can edit an existing book's information."""
        self.login("admin", "admin123")

        edit_res = self.client.post(
            "/admin/books/1/edit",
            data={
                "title": "Designing Data-Intensive Applications (2nd Edition)",
                "author": "Martin Kleppmann",
                "category_id": "1",
                "isbn": "978-1449373320",
                "published_year": "2024",
                "total_pages": "650",
                "rating": "5.0",
                "summary": "Updated guide to distributed systems.",
                "cover_gradient": "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
                "available": "1",
                "featured": "1",
            },
            follow_redirects=True,
        )
        self.assertEqual(edit_res.status_code, 200)
        self.assertIn(b"updated successfully", edit_res.data)

        # Verify update on book detail page
        detail_res = self.client.get("/books/1")
        self.assertIn(b"2nd Edition", detail_res.data)

    def test_admin_delete_book(self):
        """Verify admin can delete a book from the library."""
        self.login("admin", "admin123")

        # Delete book #4 (The Pragmatic Programmer)
        del_res = self.client.post("/admin/books/4/delete", follow_redirects=True)
        self.assertEqual(del_res.status_code, 200)
        self.assertIn(b"deleted successfully", del_res.data)

        # Confirm it is no longer in catalog
        search_res = self.client.get("/books/?q=Pragmatic")
        self.assertNotIn(b"The Pragmatic Programmer", search_res.data)

    def test_admin_prevent_delete_actively_borrowed_book(self):
        """Verify admin cannot delete a book that is currently checked out by a reader."""
        # Standard reader borrows book #1
        self.register("borrower", "borrower@example.com", "password123", "password123")
        self.login("borrower", "password123")
        self.client.post("/books/1/borrow", data={"duration": "14"}, follow_redirects=True)
        self.logout()

        # Admin attempts to delete book #1
        self.login("admin", "admin123")
        del_res = self.client.post("/admin/books/1/delete", follow_redirects=True)
        self.assertIn(b"Cannot delete", del_res.data)
        self.assertIn(b"currently borrowed", del_res.data)

    def test_admin_view_users_and_borrowings(self):
        """Verify admin can view user directory and system-wide loan audit table."""
        self.login("admin", "admin123")

        users_res = self.client.get("/admin/users")
        self.assertEqual(users_res.status_code, 200)
        self.assertIn(b"Registered Users", users_res.data)
        self.assertIn(b"admin@digirary.local", users_res.data)

        borrowings_res = self.client.get("/admin/borrowings")
        self.assertEqual(borrowings_res.status_code, 200)
        self.assertIn(b"Borrowing Records Audit", borrowings_res.data)
