from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MetricName(str, Enum):
    revenue = "revenue"
    orders_count = "orders_count"


class MetricVersion(str, Enum):
    v1 = "v1"
    v2 = "v2"


class TimeRange(str, Enum):
    last_week = "last_week"
    last_month = "last_month"
    last_quarter = "last_quarter"
    custom = "custom"


class Dimension(str, Enum):
    region = "region"
    product = "product"
    user_city = "user_city"


class FilterIntent(str, Enum):
    """
    Represents filter *requests* extracted from user language.
    Presence here does NOT imply semantic availability.
    Actual filter enforcement is metric-scoped and validated separately.
    """
    region = "region"
    product = "product"
    internal_account = "internal_account"
    refund_status = "refund_status"


class Intent(BaseModel):
    """
    Structured, enum-driven user intent.
    Anything not representable here MUST be rejected.
    """

    metric: MetricName
    version: Optional[MetricVersion] = Field(
        default=None,
        description="Metric version. If omitted, default version will be injected."
    )

    time_range: TimeRange

    dimensions: List[Dimension] = Field(default_factory=list)

    requested_filters: List[FilterIntent] = Field(default_factory=list)
