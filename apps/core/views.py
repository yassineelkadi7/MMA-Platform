"""
Core app views — home page and error handlers.
"""
from django.shortcuts import render


def home(request):
    """Platform home page — includes latest 6 news articles and featured fighters."""
    from apps.events.models import Fighter
    from apps.news.models import Article

    latest_articles = Article.objects.filter(is_hidden=False).order_by("-published_at")[:6]
    top_fighters = Fighter.objects.order_by("-wins", "losses", "-updated_at")[:4]
    return render(
        request,
        "core/home.html",
        {"latest_articles": latest_articles, "top_fighters": top_fighters},
    )


def handler404(request, exception):
    """Custom 404 error page."""
    return render(request, "core/404.html", status=404)


def handler500(request):
    """Custom 500 error page."""
    return render(request, "core/500.html", status=500)
