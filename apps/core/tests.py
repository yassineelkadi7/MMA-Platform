"""
Integration tests for the core app.
"""
from django.test import TestCase
from django.utils import timezone
from apps.accounts.models import User
from apps.core.models import APICallLog


class CSVExportTest(TestCase):
    """Integration test: log in as admin, use admin action to export API call logs as CSV,
    assert Content-Type: text/csv and correct headers."""

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
        )
        self.client.force_login(self.admin)

        # Create some API call log entries
        APICallLog.objects.create(
            endpoint="https://api.example.com/news",
            status_code=200,
            latency_ms=150,
            error_message="",
        )
        APICallLog.objects.create(
            endpoint="https://api.example.com/events",
            status_code=500,
            latency_ms=300,
            error_message="Internal Server Error",
        )

    def test_csv_export_returns_correct_content_type(self):
        # Get all log PKs
        log_pks = list(APICallLog.objects.values_list("pk", flat=True))

        response = self.client.post(
            "/admin/core/apicalllog/",
            {
                "action": "export_as_csv",
                "select_across": "0",
                "_selected_action": [str(pk) for pk in log_pks],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response["Content-Type"])

        content = response.content.decode("utf-8")
        # Check CSV headers
        self.assertIn("endpoint", content)
        self.assertIn("status_code", content)
        self.assertIn("latency_ms", content)
        self.assertIn("called_at", content)
        # Check data rows
        self.assertIn("https://api.example.com/news", content)
        self.assertIn("https://api.example.com/events", content)
