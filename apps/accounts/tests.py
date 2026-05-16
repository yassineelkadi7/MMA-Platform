"""
Integration tests for the accounts app.

Requirements: 9.5
"""
from django.test import TestCase

from apps.accounts.models import User
from apps.accounts.services import suspend_user


class SuspendedUserLoginTest(TestCase):
    """Integration test: create user, suspend via suspend_user,
    attempt login, assert redirect and no session created."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            role="amateur",
        )

    def test_suspended_user_cannot_log_in(self):
        # Suspend the user
        suspend_user(self.user)

        # Attempt login
        response = self.client.post(
            "/accounts/login/",
            {"email": "test@test.com", "password": "testpass123"},
        )

        # Should not redirect to home (login failed)
        # Should show error message (not redirect to /)
        self.assertEqual(response.status_code, 200)  # stays on login page

        # No session should be created for this user
        # The response should contain an error message
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_active_user_can_log_in(self):
        response = self.client.post(
            "/accounts/login/",
            {"email": "test@test.com", "password": "testpass123"},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        # User should be authenticated
        self.assertTrue(response.wsgi_request.user.is_authenticated)
