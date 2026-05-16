"""
Events app tasks — Celery (production) and APScheduler (development) definitions.

In production, Celery Beat drives periodic execution via CELERY_BEAT_SCHEDULE.
In development, start_events_scheduler() launches a background thread that fires
every 24 hours without requiring a running Celery worker.

# In settings/production.py, add:
# CELERY_BEAT_SCHEDULE = {
#     "sync-events-every-24h": {
#         "task": "events.sync_events_from_api",
#         "schedule": 86400.0,  # 24 hours
#     },
# }
"""

from celery import shared_task


@shared_task(name="events.sync_events_from_api")
def sync_events_task():
    """Celery task: sync events and fighters from the external sports API."""
    from apps.events.services import sync_events_from_api

    result = sync_events_from_api()
    return {
        "events_synced": result.events_synced,
        "fighters_synced": result.fighters_synced,
        "errors": result.errors,
    }


def start_events_scheduler():
    """Start the APScheduler background job for events sync (development only)."""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        sync_events_task,
        trigger=IntervalTrigger(hours=24),
        id="sync_events",
        replace_existing=True,
    )
    scheduler.start()
    return scheduler
