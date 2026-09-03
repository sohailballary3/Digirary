from datetime import date, timedelta
from tests.test_base import BaseTestCase


class TestBorrowingSystem(BaseTestCase):
    """Test book borrowing workflows, duration choices, due date logic, returns, and overdue tracking."""

    def setUp(self):
        super().setUp()
        self.register("reader1", "reader1@example.com", "password123", "password123")
        self.login("reader1", "password123")

    def test_borrow_duration_and_due_date_calculation(self):
        """Verify borrowing with duration (7, 14, 30 days) and exact due date calculation."""
        today = date.today()
        expected_due_14 = today + timedelta(days=14)

        # Borrow book #1 for 14 days
        res = self.client.post(
            "/books/1/borrow",
            data={"duration": "14"},
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Successfully borrowed", res.data)
        self.assertIn(expected_due_14.strftime("%B %d, %Y").encode("utf-8"), res.data)

        # Check in DB that book #1 is now marked unavailable
        book_res = self.client.get("/books/1")
        self.assertIn(b"Currently Checked Out", book_res.data)

        # Check dashboard displays the loan
        dash_res = self.client.get("/dashboard/")
        self.assertIn(b"Designing Data-Intensive Applications", dash_res.data)
        self.assertIn(b"14 Days", dash_res.data)

    def test_borrow_duration_7_and_30_days(self):
        """Verify 7-day and 30-day loan duration options."""
        today = date.today()

        # Borrow book #2 for 7 days
        self.client.post("/books/2/borrow", data={"duration": "7"}, follow_redirects=True)
        # Borrow book #3 for 30 days
        self.client.post("/books/3/borrow", data={"duration": "30"}, follow_redirects=True)

        dash = self.client.get("/dashboard/")
        self.assertIn(b"7 Days", dash.data)
        self.assertIn(b"30 Days", dash.data)

    def test_prevent_duplicate_borrowing(self):
        """Verify a user cannot borrow the same book twice simultaneously."""
        self.client.post("/books/1/borrow", data={"duration": "14"}, follow_redirects=True)

        # Attempt to borrow book #1 again
        dup_res = self.client.post("/books/1/borrow", data={"duration": "7"}, follow_redirects=True)
        self.assertIn(b"already borrowing", dup_res.data)

    def test_prevent_borrowing_unavailable_book(self):
        """Verify second user cannot borrow a book that is already checked out."""
        # Reader 1 borrows book #1
        self.client.post("/books/1/borrow", data={"duration": "14"}, follow_redirects=True)
        self.logout()

        # Reader 2 registers and tries to borrow book #1
        self.register("reader2", "reader2@example.com", "password123", "password123")
        self.login("reader2", "password123")

        res = self.client.post("/books/1/borrow", data={"duration": "14"}, follow_redirects=True)
        self.assertIn(b"currently borrowed and unavailable", res.data)

    def test_return_book_and_restore_availability(self):
        """Verify returning a book updates borrowing record and restores book availability."""
        # Borrow book #1
        self.client.post("/books/1/borrow", data={"duration": "14"}, follow_redirects=True)

        # Get loan ID from dashboard
        with self.app.app_context():
            from app.database import get_db
            loan = get_db().execute(
                "SELECT id FROM borrowings WHERE book_id = 1 AND status = 'active'"
            ).fetchone()
            loan_id = loan["id"]

        # Return the book
        return_res = self.client.post(
            f"/borrowings/{loan_id}/return",
            follow_redirects=True,
        )
        self.assertEqual(return_res.status_code, 200)
        self.assertIn(b"has been returned successfully", return_res.data)

        # Verify book #1 is now available again
        book_res = self.client.get("/books/1")
        self.assertIn(b"Available for Immediate Borrowing", book_res.data)

        # Verify loan appears in borrowing history
        dash_res = self.client.get("/dashboard/")
        self.assertIn(b"Borrowing History", dash_res.data)
        self.assertIn(b"Returned", dash_res.data)

    def test_prevent_unauthorized_return(self):
        """Verify user B cannot return user A's borrowed book."""
        # Reader 1 borrows book #1
        self.client.post("/books/1/borrow", data={"duration": "14"}, follow_redirects=True)

        with self.app.app_context():
            from app.database import get_db
            loan = get_db().execute(
                "SELECT id FROM borrowings WHERE book_id = 1 AND status = 'active'"
            ).fetchone()
            loan_id = loan["id"]

        self.logout()

        # Reader 2 registers and attempts to return reader 1's book
        self.register("reader2", "reader2@example.com", "password123", "password123")
        self.login("reader2", "password123")

        unauth_res = self.client.post(f"/borrowings/{loan_id}/return", follow_redirects=True)
        self.assertIn(b"Unauthorized action", unauth_res.data)
