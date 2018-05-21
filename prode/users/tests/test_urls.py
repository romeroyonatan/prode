from django.urls import reverse, resolve

from test_plus.test import TestCase


class TestUserURLs(TestCase):
    """Test URL patterns for users app."""

    def setUp(self):
        self.user = self.make_user()

    def test_list_reverse(self):
        """users:list should reverse to /usuarios/."""
        self.assertEqual(reverse("users:list"), "/usuarios/")

    def test_list_resolve(self):
        """/usuarios/ should resolve to users:list."""
        self.assertEqual(resolve("/usuarios/").view_name, "users:list")

    def test_redirect_reverse(self):
        """users:redirect should reverse to /usuarios/~redirect/."""
        self.assertEqual(reverse("users:redirect"), "/usuarios/~redirect/")

    def test_redirect_resolve(self):
        """/usuarios/~redirect/ should resolve to users:redirect."""
        self.assertEqual(resolve("/usuarios/~redirect/").view_name, "users:redirect")

    def test_detail_reverse(self):
        """users:detail should reverse to /usuarios/testuser/."""
        self.assertEqual(
            reverse("users:detail", kwargs={"username": "testuser"}), "/usuarios/testuser/"
        )

    def test_detail_resolve(self):
        """/usuarios/testuser/ should resolve to users:detail."""
        self.assertEqual(resolve("/usuarios/testuser/").view_name, "users:detail")

    def test_update_reverse(self):
        """users:update should reverse to /usuarios/~update/."""
        self.assertEqual(reverse("users:update"), "/usuarios/~update/")

    def test_update_resolve(self):
        """/usuarios/~update/ should resolve to users:update."""
        self.assertEqual(resolve("/usuarios/~update/").view_name, "users:update")
