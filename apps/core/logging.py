"""
Core logging utilities for the MMA Fighting Platform.
"""
from __future__ import annotations

from apps.core.models import APICallLog


def log_api_call(
    endpoint: str,
    status_code: int,
    latency_ms: int,
    error: str | None = None,
) -> APICallLog:
    """
    Write a single APICallLog row atomically and return the created instance.

    Args:
        endpoint: The external API endpoint that was called.
        status_code: The HTTP status code returned by the endpoint.
        latency_ms: Round-trip latency in milliseconds.
        error: Optional error message; stored as an empty string when None.

    Returns:
        The newly created APICallLog instance.
    """
    return APICallLog.objects.create(
        endpoint=endpoint,
        status_code=status_code,
        latency_ms=latency_ms,
        error_message=error or "",
    )
