"""
Events app views — fighters, events, calendar, countdown.
"""
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View

from apps.events.models import Event, Fight, Fighter
from apps.events.services import get_event_detail, get_next_event, search_fighters


class FighterListView(View):
    def get(self, request):
        q = request.GET.get("q", "")
        if q:
            fighters = search_fighters(q)
        else:
            fighters = []
        return render(
            request,
            "events/fighter_list.html",
            {"fighters": fighters, "query": q},
        )


class FighterDetailView(View):
    def get(self, request, pk):
        fighter = get_object_or_404(Fighter, pk=pk)
        fights = (
            Fight.objects.filter(Q(fighter_a=fighter) | Q(fighter_b=fighter))
            .select_related("event", "fighter_a", "fighter_b", "winner")
            .order_by("-event__date")
        )
        return render(
            request,
            "events/fighter_detail.html",
            {"fighter": fighter, "fights": fights},
        )


class EventCalendarView(View):
    """
    GET /events/calendar/       → renders the calendar HTML page
    GET /events/api/calendar/   → returns JSON array of events for the JS widget
    """
    def get(self, request):
        events = Event.objects.filter(
            status__in=["upcoming", "live", "completed"]
        ).order_by("date")[:100]
        data = [
            {
                "id": e.pk,
                "name": e.name,
                "date": e.date.isoformat(),
                "location": e.location,
                "status": e.status,
            }
            for e in events
        ]
        # If the request path contains /api/ return JSON, otherwise render page
        if "/api/" in request.path:
            return JsonResponse(data, safe=False)
        return render(request, "events/event_calendar.html", {"events_json": data})


class EventDetailView(View):
    def get(self, request, pk):
        get_object_or_404(Event, pk=pk)
        event_detail = get_event_detail(pk)
        return render(
            request,
            "events/event_detail.html",
            {"event_detail": event_detail},
        )


class CountdownAPIView(View):
    def get(self, request):
        e = get_next_event()
        if e:
            return JsonResponse(
                {
                    "event_id": e.pk,
                    "name": e.name,
                    "date": e.date.isoformat(),
                    "seconds_remaining": max(
                        0, int((e.date - timezone.now()).total_seconds())
                    ),
                }
            )
        return JsonResponse(
            {
                "event_id": None,
                "name": None,
                "date": None,
                "seconds_remaining": 0,
            }
        )
