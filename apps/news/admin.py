"""
News app admin configuration.
"""
from django.contrib import admin
from apps.news.models import Article
from apps.news.services import hide_article, fetch_and_store_articles


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "source_name", "category", "published_at", "is_hidden")
    list_filter = ("category", "is_hidden", "source_name")
    search_fields = ("title", "source_name")
    date_hierarchy = "published_at"
    actions = ["hide_selected_articles", "trigger_news_refresh"]

    @admin.action(description="Hide selected articles")
    def hide_selected_articles(self, request, queryset):
        count = 0
        for article in queryset:
            hide_article(article.pk)
            count += 1
        self.message_user(request, f"{count} article(s) hidden.")

    @admin.action(description="Trigger news refresh from External API")
    def trigger_news_refresh(self, request, queryset):
        result = fetch_and_store_articles()
        if result.errors:
            self.message_user(request, f"Refresh completed with errors: {result.errors}", level="warning")
        else:
            self.message_user(request, f"Refresh complete. {result.new_count} new article(s) fetched.")
