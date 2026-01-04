import yaml
from pathlib import Path
from typing import Dict, Tuple, Optional
from app.core.intent.schema import MetricName, MetricVersion
from .models import MetricDefinition


class MetricRegistry:
    """
    Loads, validates, and stores metric definitions.
    This is the single source of truth for business semantics.
    """

    def __init__(self, metrics_path: Path):
        self.metrics_path = metrics_path
        self._metrics: Dict[Tuple[str, str], MetricDefinition] = {}

    def load(self) -> None:
        if not self.metrics_path.exists():
            raise RuntimeError(f"Metrics path does not exist: {self.metrics_path}")

        for file in self.metrics_path.glob("*.yaml"):
            with open(file, "r", encoding="utf-8") as f:
                raw = yaml.safe_load(f)

            if raw is None:
                raise RuntimeError(f"Empty metric file: {file.name}")

            #Structural validation
            metric = MetricDefinition(**raw)

            #semantic validation
            metric.validate_semantics()

            key = (metric.metric_name, metric.version)

            if key in self._metrics:
                raise RuntimeError(
                    f"Duplicate metric definition for {metric.metric_name}:{metric.version}"
                )

            self._metrics[key] = metric

    def get(self, metric_name: str, version: Optional[str] = None) -> MetricDefinition:
        if version is None:
            version = self._default_version(metric_name)

        key = (metric_name, version)
        if key not in self._metrics:
            raise KeyError(f"Metric not found: {metric_name}:{version}")
        return self._metrics[key]


    def all_metrics(self):
        return list(self._metrics.values())
    
    def _default_version(self, metric_name: str) -> str:
        if metric_name == MetricName.revenue.value:
            return MetricVersion.v1.value
        if metric_name == MetricName.orders_count.value:
            return MetricVersion.v1.value

        raise KeyError(f"No default version defined for metric: {metric_name}")
