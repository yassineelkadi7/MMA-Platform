"""
News app tasks — Celery (production) and APScheduler (development) definitions.

In production, Celery Beat drives periodic execution via CELERY_BEAT_SCHEDULE.
In development, start_news_scheduler() launches a background thread that fires
every 60 minutes without requiring a running Celery worker.

# In settings/production.py, add:
# CELERY_BEAT_SCHEDULE = {
#     "fetch-news-every-hour": {
#         "task": "news.fetch_and_store_articles",
#         "schedule": 3600.0,  # 60 minutes
#     },
# }
"""

from celery import shared_task


@shared_task(name="news.fetch_and_store_articles")
def fetch_articles_task():
    """Celery task: fetch articles from the News API and persist new ones."""
    from apps.news.services import fetch_and_store_articles

    result = fetch_and_store_articles()
    return {"new_count": result.new_count, "errors": result.errors}


def start_news_scheduler():
    """Start the APScheduler background job for news fetching (development only)."""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        fetch_articles_task,
        trigger=IntervalTrigger(minutes=60),
        id="fetch_news",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
