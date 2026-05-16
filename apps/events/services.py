"""
Events app services — fighter search, event detail, and API sync.
"""
from dataclasses import dataclass, field
from typing import Optional

from django.utils import timezone

from apps.events.api_client import EventsAPIClient, EventsAPIError
from apps.events.models import Event, Fight, Fighter


@dataclass
class SyncResult:
    events_synced: int
    fighters_synced: int
    errors: list[str] = field(default_factory=list)


@dataclass
class EventDetail:
    event: Event
    fights: list  # list of Fight objects with prefetched fighters


def search_fighters(query: str) -> list[Fighter]:
    """
    Search for fighters by name (case-insensitive substring match).

    Args:
        query: The search string to match against fighter full names.

    Returns:
        A list of Fighter objects whose full_name contains the query.
    """
    return list(Fighter.objects.filter(full_name__icontains=query))


def get_next_event() -> Optional[Event]:
    """
    Return the nearest upcoming event by date.

    Returns:
        The Event with the smallest future date and status "upcoming",
        or None if no such event exists.
    """
    now = timezone.now()
    return (
        Event.objects.filter(date__gt=now, status="upcoming")
        .order_by("date")
        .first()
    )


def get_event_detail(event_id: int) -> EventDetail:
    """
    Retrieve an event and its full fight card.

    Args:
        event_id: Primary key of the Event to retrieve.

    Returns:
        An EventDetail containing the Event and its ordered Fight list
        with fighter_a, fighter_b, and winner pre-fetched.

    Raises:
        Event.DoesNotExist: If no event with the given pk exists.
    """
    event = Event.objects.get(pk=event_id)
    fights = (
        Fight.objects.filter(event=event)
        .select_related("fighter_a", "fighter_b", "winner")
        .order_by("bout_order")
    )
    return EventDetail(event=event, fights=list(fights))


def sync_events_from_api() -> SyncResult:
    """
    Sync events and fighters from the external sports API.

    Fetches both events and fighters from the configured API and upserts
    each record into the database using the external_id as the unique key.

    Returns:
        A SyncResult with counts of synced records and any errors encountered.
        On EventsAPIError, returns a SyncResult with zero counts and the error
        message in the errors list.
    """
    client = EventsAPIClient()

    try:
        events_data = client.fetch_events()
        fighters_data = client.fetch_fighters()
    except EventsAPIError as exc:
        return SyncResult(events_synced=0, fighters_synced=0, errors=[str(exc)])

    events_synced = 0
    for event in events_data if isinstance(events_data, list) else []:
        external_id = event.get("EventId") or event.get("external_id")
        if not external_id:
            continue
        Event.objects.update_or_create(
            external_id=str(external_id),
            defaults={
                "name": event.get("Name") or event.get("name", ""),
                "date": event.get("DateTime") or event.get("date"),
                "location": event.get("Location") or event.get("location", ""),
                "venue": event.get("Venue") or event.get("venue", ""),
                "broadcast_info": event.get("BroadcastInfo") or event.get("broadcast_info", ""),
                "status": event.get("Status") or event.get("status", "upcoming"),
            },
        )
        events_synced += 1

    fighters_synced = 0
    for fighter in fighters_data if isinstance(fighters_data, list) else []:
        external_id = fighter.get("FighterId") or fighter.get("external_id")
        if not external_id:
            continue
        Fighter.objects.update_or_create(
            external_id=str(external_id),
            defaults={
                "full_name": fighter.get("FirstName", "") + " " + fighter.get("LastName", "")
                if fighter.get("FirstName") or fighter.get("LastName")
                else fighter.get("full_name", ""),
                "nationality": fighter.get("Nationality") or fighter.get("nationality", ""),
                "fighting_style": fighter.get("FightingStyle") or fighter.get("fighting_style", ""),
                "wins": fighter.get("Wins") or fighter.get("wins", 0),
                "losses": fighter.get("Losses") or fighter.get("losses", 0),
                "draws": fighter.get("Draws") or fighter.get("draws", 0),
            },
        )
        fighters_synced += 1

    return SyncResult(
        events_synced=events_synced,
        fighters_synced=fighters_synced,
        errors=[],
    )
