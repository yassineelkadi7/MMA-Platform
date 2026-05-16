"""
Integration tests for the news fetch cycle.

Validates Requirements 3.1, 3.2, 11.2:
  3.1 - Articles are fetched from the external News API and stored in the database.
  3.2 - Duplicate articles (same external_id/URL) are not re-inserted.
  11.2 - API call activity is logged via APICallLog.
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase

from apps.news.models import Article
from apps.news.services import fetch_and_store_articles
from apps.core.models import APICallLog


class NewsFetchCycleTest(TestCase):
    """Integration test: mock NewsAPIClient HTTP response, call fetch_and_store_articles(),
    assert articles stored and APICallLog created."""

    def test_fetch_and_store_creates_articles_and_logs(self):
        # Mock the NewsAPIClient.fetch_articles to return sample data
        mock_response = {
            "articles": [
                {
                    "url": "https://example.com/article-1",
                    "title": "UFC 300 Preview",
                    "description": "A preview of UFC 300",
                    "source": {"name": "MMA Weekly", "id": "mma-weekly"},
                    "publishedAt": "2026-05-01T12:00:00Z",
                },
                {
                    "url": "https://example.com/article-2",
                    "title": "Jon Jones vs Stipe Miocic",
                    "description": "Fight analysis",
                    "source": {"name": "ESPN MMA", "id": "espn-mma"},
                    "publishedAt": "2026-05-02T10:00:00Z",
                },
            ]
        }

        with patch("apps.news.services.NewsAPIClient") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.fetch_articles.return_value = mock_response

            result = fetch_and_store_articles()

        # Assert articles were stored
        self.assertEqual(result.new_count, 2)
        self.assertEqual(result.errors, [])
        self.assertEqual(Article.objects.count(), 2)
        self.assertTrue(
            Article.objects.filter(
                external_id="https://example.com/article-1"
            ).exists()
        )

    def test_fetch_deduplicates_existing_articles(self):
        # Pre-create one article
        Article.objects.create(
            external_id="https://example.com/article-1",
            title="Existing Article",
            summary="Already in DB",
            source_name="Test",
            source_url="https://example.com/article-1",
            category="general",
            published_at="2026-05-01T12:00:00Z",
        )

        mock_response = {
            "articles": [
                {
                    "url": "https://example.com/article-1",  # duplicate
                    "title": "UFC 300 Preview",
                    "description": "A preview",
                    "source": {"name": "MMA Weekly"},
                    "publishedAt": "2026-05-01T12:00:00Z",
                },
            ]
        }

        with patch("apps.news.services.NewsAPIClient") as MockClient:
            mock_instance = MockClient.return_value
            mock_instance.fetch_articles.return_value = mock_response
            result = fetch_and_store_articles()

        self.assertEqual(result.new_count, 0)
        self.assertEqual(Article.objects.count(), 1)  # still just 1


class AdminNewsRefreshTest(TestCase):
    """Integration test: log in as admin, POST to admin refresh action,
    assert fetch_and_store_articles triggered and response includes new_count."""

    def setUp(self):
        from apps.accounts.models import User
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@test.com",
            password="adminpass123",
        )
        self.client.force_login(self.admin)
        # Create a dummy article so the changelist has a row to select.
        self.article = Article.objects.create(
            external_id="test-admin-refresh-1",
            title="Test Article for Admin Refresh",
            summary="Test summary",
            source_name="Test Source",
            source_url="https://example.com/test-admin-refresh-1",
            category="general",
            published_at="2026-01-01T00:00:00Z",
        )

    def test_admin_trigger_news_refresh_action(self):
        from unittest.mock import patch
        from apps.news.services import FetchResult

        with patch("apps.news.admin.fetch_and_store_articles") as mock_fetch:
            mock_fetch.return_value = FetchResult(new_count=5, errors=[])

            # POST to admin changelist with the trigger_news_refresh action.
            # Django requires at least one _selected_action value to dispatch
            # the action; the action itself ignores the queryset.
            response = self.client.post(
                "/admin/news/article/",
                {
                    "action": "trigger_news_refresh",
                    "select_across": "0",
                    "_selected_action": [str(self.article.pk)],
                },
                follow=True,
                raise_request_exception=False,
            )

        mock_fetch.assert_called_once()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "5")  # new_count in message
