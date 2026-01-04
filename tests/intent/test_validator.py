from pathlib import Path

from app.core.intent.schema import Intent, MetricName, TimeRange, Dimension
from app.core.intent.validator import IntentValidator, IntentValidationError
from app.core.metrics.registry import MetricRegistry


def test_valid_intent_passes():
    registry = MetricRegistry(
        Path(__file__).resolve().parents[2] / "metadata" / "metrics"
    )
    registry.load()

    intent = Intent(
        metric=MetricName.revenue,
        time_range=TimeRange.last_month,
        dimensions=[Dimension.region],
        requested_filters=[]
    )

    validator = IntentValidator(registry)
    validator.validate(intent)


def test_forbidden_filter_rejected():
    registry = MetricRegistry(
        Path(__file__).resolve().parents[2] / "metadata" / "metrics"
    )
    registry.load()

    intent = Intent(
        metric=MetricName.revenue,
        time_range=TimeRange.last_month,
        dimensions=[],
        requested_filters=["internal_account"]
    )

    validator = IntentValidator(registry)

    try:
        validator.validate(intent)
        assert False, "Expected rejection"
    except IntentValidationError:
        pass
