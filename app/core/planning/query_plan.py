from typing import List
from pydantic import BaseModel


class JoinPlan(BaseModel):
    left: str
    right: str
    type: str


class FilterPlan(BaseModel):
    column: str
    operator: str
    value: str


class QueryPlan(BaseModel):
    """
    Deterministic representation of a query.
    This is the ONLY object allowed to drive SQL generation.
    """

    metric_name: str
    metric_version: str

    fact_table: str

    joins: List[JoinPlan]

    measure_expression: str
    aggregation: str

    filters: List[FilterPlan]

    group_by: List[str]

    time_column: str
    time_range: str
