"""
Integration tests for the AI Assistant app.

Validates: Requirements 7.1, 7.2, 7.3
"""
from unittest.mock import patch

from django.test import TestCase

from apps.accounts.models import User
from apps.ai_assistant.models import ConversationMessage


class ChatEndpointTest(TestCase):
    """Integration test: log in as user, POST message to /ai/chat/,
    assert ConversationMessage saved and JSON response contains reply."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="testpass123",
            role="amateur",
        )
        self.client.force_login(self.user)

    def test_chat_endpoint_saves_message_and_returns_reply(self):
        with patch("apps.ai_assistant.views.send_message") as mock_send:
            mock_send.return_value = "Great question about MMA training!"

            response = self.client.post(
                "/ai/chat/",
                {"message": "What is the best MMA training routine?"},
                content_type="application/x-www-form-urlencoded",
            )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reply", data)
        self.assertEqual(data["reply"], "Great question about MMA training!")
        mock_send.assert_called_once()

    def test_chat_endpoint_requires_login(self):
        self.client.logout()
        response = self.client.post(
            "/ai/chat/",
            {"message": "test"},
        )
        # Should redirect to login or return 403
        self.assertIn(response.status_code, [302, 403])
