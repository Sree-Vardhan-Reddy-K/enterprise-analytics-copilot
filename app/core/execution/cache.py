from typing import Any, Tuple
from cachetools import TTLCache

from app.core.intent.schema import Intent


class QueryCache:
    """
    Deterministic cache keyed by semantic intent, not SQL text.
    """

    def __init__(self, maxsize: int = 512, ttl_seconds: int = 300):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    def _make_key(self, intent: Intent, metric_version: str) -> Tuple[Any, ...]:
        return (
            intent.metric.value,
            metric_version,
            intent.time_range.value,
            tuple(sorted(d.value for d in intent.dimensions)),
            tuple(sorted(f.value for f in intent.requested_filters)),
        )

    def get(self, intent: Intent, metric_version: str):
        key = self._make_key(intent, metric_version)
        return self._cache.get(key)

    def set(self, intent: Intent, metric_version: str, value):
        key = self._make_key(intent, metric_version)
        self._cache[key] = value
