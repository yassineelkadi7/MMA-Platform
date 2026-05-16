"""
News API client for the MMA Fighting Platform.

Tries GNews API first (works server-side, free tier 100 req/day).
Falls back to NewsAPI if GNews key is not set.
Records latency and status for every request via core logging utilities.
"""
import time

import requests
from django.conf import settings

from apps.core.logging import log_api_call


class NewsAPIError(Exception):
    """Raised when the News API returns an error or the request fails."""


class NewsAPIClient:
    """
    Fetches MMA news articles.

    Priority:
      1. GNews API  (https://gnews.io) — works server-side, free 100 req/day
      2. NewsAPI    (https://newsapi.org) — free plan blocks server-side requests
    """

    GNEWS_URL = "https://gnews.io/api/v4/search"
    NEWSAPI_URL = "https://newsapi.org/v2/everything"

    def __init__(self):
        self.news_api_key = settings.NEWS_API_KEY
        self.gnews_api_key = getattr(settings, "GNEWS_API_KEY", "")

    def fetch_articles(self, query: str = "MMA UFC boxing martial arts", page_size: int = 20) -> dict:
        """
        Fetch articles. Tries GNews first, falls back to NewsAPI.

        Returns a normalised dict with an "articles" list compatible with
        the existing NewsFetchService parser.
        """
        # Try GNews if key is available
        if self.gnews_api_key and self.gnews_api_key != "your-gnews-api-key-here":
            try:
                return self._fetch_gnews(query, page_size)
            except NewsAPIError:
                pass  # fall through to NewsAPI

        # Fall back to NewsAPI
        return self._fetch_newsapi(query, page_size)

    def _fetch_gnews(self, query: str, page_size: int) -> dict:
        """Fetch from GNews API and normalise to NewsAPI format."""
        params = {
            "q": query,
            "lang": "en",
            "max": min(page_size, 10),  # GNews free tier max is 10
            "apikey": self.gnews_api_key,
        }
        start = time.time()
        try:
            resp = requests.get(self.GNEWS_URL, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            latency_ms = int((time.time() - start) * 1000)
            log_api_call(self.GNEWS_URL, 0, latency_ms, error=str(exc))
            raise NewsAPIError(f"GNews request failed: {exc}") from exc

        latency_ms = int((time.time() - start) * 1000)

        if resp.status_code >= 400:
            log_api_call(self.GNEWS_URL, resp.status_code, latency_ms, error=resp.text[:200])
            raise NewsAPIError(f"GNews returned HTTP {resp.status_code}")

        log_api_call(self.GNEWS_URL, resp.status_code, latency_ms)
        data = resp.json()

        # Normalise GNews format → NewsAPI format
        articles = []
        for a in data.get("articles", []):
            articles.append({
                "url": a.get("url", ""),
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "content": a.get("content", ""),
                "source": {"name": a.get("source", {}).get("name", ""), "id": None},
                "publishedAt": a.get("publishedAt", ""),
                "urlToImage": a.get("image", ""),
            })
        return {"articles": articles, "totalResults": len(articles)}

    def _fetch_newsapi(self, query: str, page_size: int) -> dict:
        """Fetch from NewsAPI."""
        params = {
            "q": query,
            "pageSize": page_size,
            "apiKey": self.news_api_key,
            "language": "en",
            "sortBy": "publishedAt",
        }
        start = time.time()
        try:
            resp = requests.get(self.NEWSAPI_URL, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            latency_ms = int((time.time() - start) * 1000)
            log_api_call(self.NEWSAPI_URL, 0, latency_ms, error=str(exc))
            raise NewsAPIError(f"NewsAPI request failed: {exc}") from exc

        latency_ms = int((time.time() - start) * 1000)

        if resp.status_code >= 400:
            log_api_call(self.NEWSAPI_URL, resp.status_code, latency_ms, error=resp.text[:200])
            raise NewsAPIError(
                f"NewsAPI returned HTTP {resp.status_code}: {resp.text[:200]}"
            )

        log_api_call(self.NEWSAPI_URL, resp.status_code, latency_ms)
        return resp.json()
