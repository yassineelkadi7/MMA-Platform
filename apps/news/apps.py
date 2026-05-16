import threading
import logging

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class NewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.news"
    verbose_name = "News"

    def ready(self):
        """Start the background news refresh thread when the server starts."""
        import os
        # Only run in the main process (not the reloader child process)
        if os.environ.get("RUN_MAIN") != "true":
            return
        self._start_news_scheduler()

    def _start_news_scheduler(self):
        """Fetch news immediately on startup, then every 60 minutes."""
        def run():
            import time
            # Wait 5 seconds for Django to fully initialise before first fetch
            time.sleep(5)
            while True:
                try:
                    from apps.news.services import fetch_and_store_articles
                    result = fetch_and_store_articles()
                    if result.errors:
                        logger.warning("News fetch errors: %s", result.errors)
                    else:
                        logger.info("News fetch complete: %d new articles", result.new_count)
                except Exception as exc:
                    logger.error("News fetch failed: %s", exc)
                # Wait 60 minutes before next fetch
                time.sleep(60 * 60)

        thread = threading.Thread(target=run, daemon=True, name="news-refresh")
        thread.start()
        logger.info("News auto-refresh thread started (every 60 minutes)")
