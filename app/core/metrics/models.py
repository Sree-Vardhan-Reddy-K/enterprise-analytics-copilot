from typing import List, Literal
from pydantic import BaseModel, Field, validator

JoinType = Literal["inner", "left", "right"]


class JoinDefinition(BaseModel):
    left: str
    right: str
    type: JoinType


class MeasureDefinition(BaseModel):
    expression: str
    aggregation: Literal["sum", "count", "avg", "min", "max"]

    @validator("expression")
    def no_nested_aggregates(cls, v):
        lowered = v.lower()
        if "sum(" in lowered or "avg(" in lowered or "count(" in lowered:
            raise ValueError(
                "expression must reference raw columns, not aggregated expressions"
            )
        return v


class FilterDefinition(BaseModel):
    column: str
    operator: Literal["=", "!=", ">", ">=", "<", "<="]
    value: str


class MetricDefinition(BaseModel):
    metric_name: str
    version: str
    description: str

    grain: str
    time_column: str

    tables: dict
    joins: list[JoinDefinition]

    measure: MeasureDefinition

    required_filters: List[FilterDefinition]
    allowed_filters: List[str]
    forbidden_filters: List[str]

    supports_dimensions: bool = Field(default=False)
    pii_exposure: bool = Field(default=False)

    #EXISTING VALIDATORS

    @validator("allowed_filters")
    def no_overlap_with_forbidden(cls, v, values):
        forbidden = set(values.get("forbidden_filters", []))
        overlap = forbidden.intersection(set(v))
        if overlap:
            raise ValueError(
                f"Filters {overlap} cannot be both allowed and forbidden"
            )
        return v

    @validator("time_column")
    def time_column_must_be_explicit(cls, v):
        if not v or "." not in v:
            raise ValueError(
                "time_column must be fully qualified (e.g., orders.order_date)"
            )
        return v

    @validator("grain")
    def grain_must_be_single_column(cls, v):
        if "." not in v:
            raise ValueError(
                "grain must be a fully qualified column (e.g., orders.order_id)"
            )
        return v

    #SEMANTIC VALIDATION

    def validate_semantics(self) -> None:
        """
        Enforce business invariants that go beyond schema validation.
        """

        if not self.grain:
            raise ValueError("Metric must define grain")

        if not self.time_column:
            raise ValueError("Metric must define time_column")

        required_filter_names = {f.column.split(".")[-1] for f in self.required_filters}

        if not required_filter_names.issubset(set(self.allowed_filters)):
            raise ValueError(
                "All required_filters must be included in allowed_filters"
            )



