"""
Custom admin views for the core app.
"""
from datetime import timedelta

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from apps.core.models import APICallLog


@method_decorator(staff_member_required, name="dispatch")
class APIMonitorDashboardView(View):
    """
    Admin dashboard view for monitoring outbound API call health.

    Displays aggregate statistics for the last 24 hours and 30 days,
    the overall success rate, and the most recent error entry.
    """

    def get(self, request):
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_30d = now - timedelta(days=30)

        total_24h = APICallLog.objects.filter(called_at__gte=last_24h).count()
        total_30d = APICallLog.objects.filter(called_at__gte=last_30d).count()

        success_24h = APICallLog.objects.filter(
            called_at__gte=last_24h, status_code__lt=400
        ).count()
        success_rate = round((success_24h / total_24h * 100), 1) if total_24h > 0 else 0

        last_error = (
            APICallLog.objects.filter(status_code__gte=400)
            .order_by("-called_at")
            .first()
        )

        context = {
            "title": "API Monitor Dashboard",
            "total_24h": total_24h,
            "total_30d": total_30d,
            "success_rate": success_rate,
            "last_error": last_error,
        }
        return render(request, "admin/api_monitor.html", context)
