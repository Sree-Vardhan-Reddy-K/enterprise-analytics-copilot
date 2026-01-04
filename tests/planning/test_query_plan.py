from pathlib import Path

from app.core.intent.schema import Intent, MetricName, TimeRange, Dimension
from app.core.metrics.registry import MetricRegistry
from app.core.planning.builder import QueryPlanBuilder


def test_query_plan_is_deterministic():
    registry = MetricRegistry(
        Path(__file__).resolve().parents[2] / "metadata" / "metrics"
    )
    registry.load()

    metric = registry.get("revenue", "v1")

    intent = Intent(
        metric=MetricName.revenue,
        time_range=TimeRange.last_month,
        dimensions=[Dimension.region],
        requested_filters=[]
    )

    plan = QueryPlanBuilder().build(intent, metric)

    assert plan.fact_table == "orders"
    assert plan.aggregation == "sum"
    assert "orders.status" in [f.column for f in plan.filters]
    assert plan.group_by == ["region"]
