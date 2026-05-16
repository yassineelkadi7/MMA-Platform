"""
Management command to manually trigger a news fetch from the External API.

Usage:
    python manage.py fetch_news
"""
from django.core.management.base import BaseCommand
from apps.news.services import fetch_and_store_articles


class Command(BaseCommand):
    help = "Fetch MMA news articles from the External API and store them in the database."

    def handle(self, *args, **options):
        self.stdout.write("Fetching news articles...")
        result = fetch_and_store_articles()
        if result.errors:
            self.stderr.write(
                self.style.ERROR(f"Errors during fetch: {result.errors}")
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. {result.new_count} new article(s) fetched."
            )
        )
