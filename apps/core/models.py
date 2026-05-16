"""
Core app models — shared base models and API call logging.
"""
from django.db import models


class APICallLog(models.Model):
    """
    Records every outbound external API call for observability and admin monitoring.

    Tracks the endpoint called, the HTTP status code returned, the round-trip
    latency in milliseconds, an optional error message, and the timestamp of
    the call.
    """

    endpoint = models.CharField(max_length=500)
    status_code = models.PositiveSmallIntegerField()
    latency_ms = models.PositiveIntegerField()
    error_message = models.TextField(blank=True)
    called_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-called_at"]
        indexes = [
            models.Index(fields=["called_at", "status_code"], name="core_apicall_called_status_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.endpoint} [{self.status_code}] @ {self.called_at}"
