from tests.test_base import BaseTestCase


class TestBooksCatalogue(BaseTestCase):
    """Test book listing, search queries, category filters, and detail views."""

    def test_book_listing_accessible_without_login(self):
        """Verify public catalogue is accessible to unauthenticated visitors."""
        response = self.client.get("/books/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Digital Book Catalogue", response.data)
        self.assertIn(b"Designing Data-Intensive Applications", response.data)
        self.assertIn(b"Clean Code", response.data)

    def test_book_search_by_title(self):
        """Verify search by book title."""
        res = self.client.get("/books/?q=Astrophysics")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Astrophysics for People in a Hurry", res.data)
        self.assertNotIn(b"Clean Code: A Handbook", res.data)

    def test_book_search_by_author(self):
        """Verify search by author name."""
        res = self.client.get("/books/?q=Harari")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Sapiens", res.data)
        self.assertNotIn(b"Marcus Aurelius", res.data)

    def test_book_filter_by_category(self):
        """Verify category slug filtering."""
        res = self.client.get("/books/?category=philosophy")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Meditations", res.data)
        self.assertNotIn(b"Designing Data-Intensive Applications", res.data)

    def test_book_detail_view(self):
        """Verify individual book details page."""
        res = self.client.get("/books/1")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Designing Data-Intensive Applications", res.data)
        self.assertIn(b"Martin Kleppmann", res.data)
        self.assertIn(b"Synopsis & Overview", res.data)
        self.assertIn(b"Available for Immediate Borrowing", res.data)

    def test_book_detail_nonexistent_404(self):
        """Verify 404 response for nonexistent book ID."""
        res = self.client.get("/books/99999")
        self.assertEqual(res.status_code, 404)
        self.assertIn(b"Volume Not Found", res.data)
