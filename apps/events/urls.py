"""
Events app URL configuration.
"""
from django.urls import path

from apps.events.views import (
    CountdownAPIView,
    EventCalendarView,
    EventDetailView,
    FighterDetailView,
    FighterListView,
)

app_name = "events"

urlpatterns = [
    path("fighters/", FighterListView.as_view(), name="fighter_list"),
    path("fighters/<int:pk>/", FighterDetailView.as_view(), name="fighter_detail"),
    path("calendar/", EventCalendarView.as_view(), name="calendar"),
    path("<int:pk>/", EventDetailView.as_view(), name="event_detail"),
    path("api/countdown/", CountdownAPIView.as_view(), name="countdown"),
    path("api/calendar/", EventCalendarView.as_view(), name="calendar_api"),
]
