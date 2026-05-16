"""
Core caching utilities for the MMA Fighting Platform.
"""
from __future__ import annotations

from typing import Any, Callable

from django.core.cache import cache


def get_or_fetch(key: str, fetch_fn: Callable, ttl_seconds: int) -> Any:
    """
    Return the cached value for *key*, or call *fetch_fn* to populate it.

    Checks Django's cache for *key* first. If a cached value is found it is
    returned immediately without calling *fetch_fn*. If the key is absent,
    *fetch_fn* is called with no arguments, the result is stored in the cache
    with the given TTL, and then returned to the caller.

    Args:
        key: The cache key to look up / store under.
        fetch_fn: A zero-argument callable that produces the value to cache
                  when the key is not present.
        ttl_seconds: Time-to-live for the cached entry, in seconds.

    Returns:
        The cached value (if present) or the freshly fetched value.
    """
    cached = cache.get(key)
    if cached is not None:
        return cached

    result = fetch_fn()
    cache.set(key, result, ttl_seconds)
    return result
