from app.core.execution.cache import QueryCache
from app.core.intent.schema import Intent, MetricName, TimeRange


def test_cache_key_is_order_independent():
    cache = QueryCache()

    intent1 = Intent(
        metric=MetricName.revenue,
        time_range=TimeRange.last_month,
        dimensions=[],
        requested_filters=[]
    )

    intent2 = Intent(
        metric=MetricName.revenue,
        time_range=TimeRange.last_month,
        dimensions=[],
        requested_filters=[]
    )

    cache.set(intent1, "v1", 123)

    assert cache.get(intent2, "v1") == 123
