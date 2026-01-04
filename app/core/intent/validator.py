from typing import Set

from pydantic import ValidationError

from .schema import Intent, MetricName, MetricVersion, TimeRange, Dimension, FilterIntent
from app.core.metrics.registry import MetricRegistry


class IntentValidationError(Exception):
    """Raised when user intent violates system constraints."""


class IntentValidator:
    """
    Validates structured intent against business rules and metric definitions.
    This layer rejects ambiguity and unsupported requests.
    """

    def __init__(self, metric_registry: MetricRegistry):
        self.metric_registry = metric_registry

    def validate(self, intent: Intent) -> None:
        """
        Validate intent. Raises IntentValidationError on failure.
        """        

        metric_version = intent.version or self._default_version(intent.metric)

        metric = self.metric_registry.get(
            intent.metric.value,
            metric_version.value,
        )

        if metric.pii_exposure:
            raise IntentValidationError(
                "This metric is marked as PII-exposing and cannot be queried."
            )

        # Dimension capability enforcement-- scalar KPI enforcement

        if intent.dimensions and not metric.supports_dimensions:
            raise IntentValidationError(
                "This metric does not support dimensional breakdowns."
            )


        self._validate_filters(intent, metric)
        self._validate_time_range(intent)


    def _default_version(self, metric: MetricName) -> MetricVersion:
        """
        Inject default metric version.
        Defaults are explicit and auditable.
        """
        # Hardcoded defaults for now; later can be config-driven
        if metric == MetricName.revenue:
            return MetricVersion.v1
        if metric == MetricName.orders_count:
            return MetricVersion.v1

        raise IntentValidationError(f"No default version for metric: {metric}")



    def _validate_filters(self, intent: Intent, metric) -> None:
        allowed = set(metric.allowed_filters)
        forbidden = set(metric.forbidden_filters)

        for f in intent.requested_filters:
            if f.value in forbidden:
                raise IntentValidationError(
                    f"Filter '{f.value}' is forbidden for metric "
                    f"{metric.metric_name}:{metric.version}"
                )

            if f.value not in allowed:
                raise IntentValidationError(
                    f"Filter '{f.value}' is not supported for metric "
                    f"{metric.metric_name}:{metric.version}"
                )

    def _validate_time_range(self, intent: Intent) -> None:
        # All metrics currently require a time range
        if intent.time_range is None:
            raise IntentValidationError("Time range is required for all queries")

        if intent.time_range == TimeRange.custom:
            # Custom ranges are handled explicitly later
            raise IntentValidationError(
                "Custom time ranges are not supported yet"
            )
