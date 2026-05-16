"""
Events API client for the MMA Fighting Platform.

Fetches MMA event and fighter data from the SportsData.io API and records
latency and status for every request via the core logging utilities.
"""
import time

import requests
from django.conf import settings

from apps.core.logging import log_api_call


class EventsAPIError(Exception):
    """Raised when the Sports API returns an error or the request fails."""


class EventsAPIClient:
    """Thin wrapper around the SportsData.io MMA scores/json endpoints."""

    def __init__(self):
        self.api_key = settings.SPORTS_API_KEY
        self.base_url = "https://api.sportsdata.io/v3/mma/scores/json"

    def fetch_events(self, league: str = "UFC") -> dict:
        """
        Fetch upcoming events from the sports API.

        Args:
            league: The league identifier to query (e.g. "UFC").

        Returns:
            Raw JSON response as a dict.

        Raises:
            EventsAPIError: On any network error or non-2xx HTTP response.
        """
        endpoint = f"{self.base_url}/Schedule/{league}"
        params = {"key": self.api_key}

        start_time = time.time()
        try:
            response = requests.get(endpoint, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            latency_ms = int((time.time() - start_time) * 1000)
            log_api_call(endpoint, 0, latency_ms)
            raise EventsAPIError(f"Request to Sports API failed: {exc}") from exc

        latency_ms = int((time.time() - start_time) * 1000)

        if response.status_code >= 400:
            log_api_call(
                endpoint,
                response.status_code,
                latency_ms,
                error=response.text[:200],
            )
            raise EventsAPIError(
                f"Sports API returned HTTP {response.status_code}: {response.text[:200]}"
            )

        log_api_call(endpoint, response.status_code, latency_ms)
        return response.json()

    def fetch_fighters(self, fighter_id=None) -> dict:
        """
        Fetch fighter data from the sports API.

        Args:
            fighter_id: Optional fighter ID to fetch a specific fighter.
                        If None, fetches all fighters.

        Returns:
            Raw JSON response as a dict.

        Raises:
            EventsAPIError: On any network error or non-2xx HTTP response.
        """
        if fighter_id is not None:
            endpoint = f"{self.base_url}/Fighter/{fighter_id}"
        else:
            endpoint = f"{self.base_url}/Fighters"
        params = {"key": self.api_key}

        start_time = time.time()
        try:
            response = requests.get(endpoint, params=params, timeout=10)
        except requests.exceptions.RequestException as exc:
            latency_ms = int((time.time() - start_time) * 1000)
            log_api_call(endpoint, 0, latency_ms)
            raise EventsAPIError(f"Request to Sports API failed: {exc}") from exc

        latency_ms = int((time.time() - start_time) * 1000)

        if response.status_code >= 400:
            log_api_call(
                endpoint,
                response.status_code,
                latency_ms,
                error=response.text[:200],
            )
            raise EventsAPIError(
                f"Sports API returned HTTP {response.status_code}: {response.text[:200]}"
            )

        log_api_call(endpoint, response.status_code, latency_ms)
        return response.json()
