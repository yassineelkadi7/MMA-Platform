"""
Core app admin configuration.
"""
import csv
from django.contrib import admin
from django.http import HttpResponse
from apps.core.models import APICallLog


@admin.register(APICallLog)
class APICallLogAdmin(admin.ModelAdmin):
    list_display = ("endpoint", "status_code", "latency_ms", "error_message", "called_at")
    list_filter = ("status_code",)
    date_hierarchy = "called_at"
    readonly_fields = ("endpoint", "status_code", "latency_ms", "error_message", "called_at")
    actions = ["export_as_csv"]

    @admin.action(description="Export selected API call logs as CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="api_call_logs.csv"'

        writer = csv.writer(response)
        writer.writerow(["endpoint", "status_code", "latency_ms", "error_message", "called_at"])

        for log in queryset.order_by("-called_at"):
            writer.writerow([
                log.endpoint,
                log.status_code,
                log.latency_ms,
                log.error_message,
                log.called_at.isoformat(),
            ])

        return response
