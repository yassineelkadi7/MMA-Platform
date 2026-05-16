"""
News app views — news listing and detail.
"""
from django.shortcuts import get_object_or_404, render
from django.views import View

from apps.news.models import Article
from apps.news.services import get_articles


class NewsListView(View):
    """Display a paginated list of news articles, optionally filtered by category."""

    def get(self, request):
        category = request.GET.get("category")
        page = request.GET.get("page", 1)
        page_obj = get_articles(category=category or None, page=page)
        return render(
            request,
            "news/list.html",
            {
                "page_obj": page_obj,
                "category": category,
                "categories": Article.CATEGORY_CHOICES,
            },
        )


class NewsDetailView(View):
    """Display a single news article."""

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk, is_hidden=False)
        return render(request, "news/detail.html", {"article": article})
