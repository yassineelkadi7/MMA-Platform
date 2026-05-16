"""
News app services — fetch, store, and manage articles.
"""
import hashlib
from dataclasses import dataclass, field

from django.core.paginator import Paginator
from django.utils.dateparse import parse_datetime

from apps.news.api_client import NewsAPIClient, NewsAPIError
from apps.news.models import Article


@dataclass
class FetchResult:
    new_count: int
    errors: list[str] = field(default_factory=list)


def _build_external_id(article: dict) -> str:
    """
    Derive a stable external identifier for a NewsAPI article.

    Prefers the article URL directly; falls back to a combination of the
    source id and a short hash of the title so that every article gets a
    unique, deterministic key even when the URL is absent.
    """
    url = article.get("url")
    if url:
        return url

    source_id = article.get("source", {}).get("id") or ""
    title = article.get("title", "")
    title_hash = hashlib.md5(title.encode("utf-8")).hexdigest()[:12]
    return f"{source_id}:{title_hash}"


def fetch_and_store_articles() -> FetchResult:
    """
    Fetch articles from the News API and persist new ones to the database.

    Returns:
        FetchResult with the count of newly inserted articles and any errors.
    """
    try:
        client = NewsAPIClient()
        response = client.fetch_articles()
    except NewsAPIError as exc:
        return FetchResult(new_count=0, errors=[str(exc)])

    raw_articles = response.get("articles", [])

    # Build candidate Article objects from the raw payload.
    candidates: list[Article] = []
    for article in raw_articles:
        external_id = _build_external_id(article)
        title = article.get("title", "")
        summary = article.get("description", "") or article.get("content", "") or ""
        source_name = article.get("source", {}).get("name", "")
        source_url = article.get("url", "")
        image_url = article.get("urlToImage", "") or article.get("image", "") or ""
        category = "general"
        published_at = parse_datetime(article.get("publishedAt", "") or "")

        if published_at is None:
            continue

        candidates.append(
            Article(
                external_id=external_id,
                title=title,
                summary=summary,
                source_name=source_name,
                source_url=source_url,
                image_url=image_url,
                category=category,
                published_at=published_at,
            )
        )

    if not candidates:
        return FetchResult(new_count=0, errors=[])

    # Deduplicate against existing records.
    candidate_ids = [a.external_id for a in candidates]
    existing_ids = set(
        Article.objects.filter(external_id__in=candidate_ids).values_list(
            "external_id", flat=True
        )
    )

    new_articles = [a for a in candidates if a.external_id not in existing_ids]

    if new_articles:
        Article.objects.bulk_create(new_articles, ignore_conflicts=True)

    return FetchResult(new_count=len(new_articles), errors=[])


def get_articles(category: str | None = None, page: int = 1):
    """
    Return a paginated page of visible articles.

    Args:
        category: Optional category slug to filter by.
        page:     1-based page number.

    Returns:
        A Django Page object containing up to 20 Article instances.
    """
    queryset = Article.objects.filter(is_hidden=False)
    if category is not None:
        queryset = queryset.filter(category=category)
    queryset = queryset.order_by("-published_at")
    paginator = Paginator(queryset, 20)
    return paginator.get_page(page)


def hide_article(article_id: int) -> None:
    """
    Mark an article as hidden so it no longer appears in public listings.

    Args:
        article_id: Primary key of the Article to hide.

    Raises:
        Article.DoesNotExist: If no article with the given pk exists.
    """
    article = Article.objects.get(pk=article_id)
    article.is_hidden = True
    article.save()
