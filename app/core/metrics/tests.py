from pathlib import Path

from .registry import MetricRegistry


METRICS_PATH = Path(__file__).resolve().parents[3] / "metadata" / "metrics"


def test_all_metrics_load_and_validate():
    """
    Every metric must:
    - load successfully
    - pass Pydantic validation
    """
    registry = MetricRegistry(METRICS_PATH)
    registry.load()

    assert len(registry.all_metrics()) > 0, "No metrics loaded"


def test_revenue_has_required_completed_filter():
    """
    Revenue must always filter completed orders.
    This invariant must NEVER be broken.
    """
    registry = MetricRegistry(METRICS_PATH)
    registry.load()

    revenue = registry.get("revenue", "v1")

    filters = {
        f"{f.column} {f.operator} {f.value}"
        for f in revenue.required_filters
    }

    assert (
        "orders.status = COMPLETED" in filters
    ), "Revenue metric must filter COMPLETED orders"


def test_no_metric_allows_forbidden_filters():
    """
    Forbidden filters must never appear in allowed_filters.
    """
    registry = MetricRegistry(METRICS_PATH)
    registry.load()

    for metric in registry.all_metrics():
        overlap = set(metric.allowed_filters).intersection(
            set(metric.forbidden_filters)
        )
        assert not overlap, (
            f"{metric.metric_name}:{metric.version} "
            f"has forbidden filters enabled: {overlap}"
        )


def test_time_column_is_single_and_explicit():
    """
    Each metric must declare exactly one authoritative time column.
    """
    registry = MetricRegistry(METRICS_PATH)
    registry.load()

    for metric in registry.all_metrics():
        assert "." in metric.time_column, (
            f"{metric.metric_name}:{metric.version} "
            "time_column must be fully qualified"
        )
