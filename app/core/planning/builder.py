from typing import List

from app.core.intent.schema import Intent
from app.core.metrics.models import MetricDefinition, FilterDefinition
from .query_plan import QueryPlan, JoinPlan, FilterPlan


class QueryPlanBuilder:
    """
    Builds a deterministic QueryPlan from validated intent and metric metadata.
    No SQL generation happens here.
    """

    def build(self, intent: Intent, metric: MetricDefinition) -> QueryPlan:
        joins = [
            JoinPlan(
                left=j.left,
                right=j.right,
                type=j.type,
            )
            for j in metric.joins
        ]

        filters: List[FilterPlan] = []

        #Required filters from metric definition
        for rf in metric.required_filters:
            filters.append(
                FilterPlan(
                    column=rf.column,
                    operator=rf.operator,
                    value=rf.value,
                )
            )

        # User-requested filters
        for f in intent.requested_filters:
            filters.append(
                FilterPlan(
                    column=f.value,
                    operator="IS NOT",
                    value="NULL",
                )
            )


        # Group-by comes ONLY from dimensions
        group_by = [dim.value for dim in intent.dimensions]

        return QueryPlan(
            metric_name=metric.metric_name,
            metric_version=metric.version,
            fact_table=metric.tables["fact"],
            joins=joins,
            measure_expression=metric.measure.expression,
            aggregation=metric.measure.aggregation,
            filters=filters,
            group_by=group_by,
            time_column=metric.time_column,
            time_range=intent.time_range.value,
        )
