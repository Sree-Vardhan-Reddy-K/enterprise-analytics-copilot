from pathlib import Path
from fastapi import FastAPI, HTTPException

from app.core.metrics.registry import MetricRegistry
from app.core.intent.extractor import IntentExtractor
from app.core.intent.validator import IntentValidator, IntentValidationError
from app.core.planning.builder import QueryPlanBuilder
from app.core.sql.generator import SQLGenerator
from app.core.sql.validator import SQLValidator, SQLValidationError
from app.core.execution.cache import QueryCache
from app.llm.client import LLMClient
from app.config.database import get_database_url
from app.core.execution.db import Database

database = Database(get_database_url())



app = FastAPI(title="Enterprise Analytics Copilot")


#GLOBAL SINGLETONS (intentional, read-only semantics)

METRICS_PATH = Path(__file__).resolve().parents[1] / "metadata" / "metrics"

metric_registry = MetricRegistry(METRICS_PATH)
metric_registry.load()

intent_validator = IntentValidator(metric_registry)
query_plan_builder = QueryPlanBuilder()
sql_validator = SQLValidator()
cache = QueryCache()

# LLM client will be mocked initially
llm_client = LLMClient()
intent_extractor = IntentExtractor(llm_client)
sql_generator = SQLGenerator(llm_client)


@app.get("/health")
def health():
    return {"status": "ok"}


from app.api.query import router as query_router
app.include_router(query_router)
