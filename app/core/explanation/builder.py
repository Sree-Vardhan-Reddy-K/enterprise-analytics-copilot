from typing import Dict

from app.core.intent.schema import Intent
from app.core.metrics.models import MetricDefinition
from app.core.planning.query_plan import QueryPlan


class ExplanationBuilder:
    """
    Builds a deterministic explanation for a query result.
    No LLM logic. No inference.
    """

    def build(
        self,
        intent: Intent,
        metric: MetricDefinition,
        plan: QueryPlan,
    ) -> Dict[str, str]:

        explanation = {
            "metric": f"{metric.metric_name} ({metric.version})",
            "description": metric.description,
            "time_range": intent.time_range.value,
            "grain": metric.grain,
            "aggregation": f"{plan.aggregation.upper()}({plan.measure_expression})",
            "filters_applied": self._filters(metric),
            "grouped_by": ", ".join(plan.group_by) if plan.group_by else "none",
            "data_sources": ", ".join(
                [metric.tables["fact"]] +
                metric.tables.get("dimensions", [])
            ),
        }

        return explanation

    def _filters(self, metric: MetricDefinition) -> str:
        parts = []
        for f in metric.required_filters:
            value = f"'{f.value}'" if isinstance(f.value, str) else f.value
            parts.append(f"{f.column} {f.operator} {value}")

        return "; ".join(parts) if parts else "none"
