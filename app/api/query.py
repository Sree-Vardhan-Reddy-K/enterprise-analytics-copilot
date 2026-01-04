from fastapi import APIRouter, HTTPException

from app.core.explanation.builder import ExplanationBuilder
from app.core.intent.extractor import IntentExtractionError
from app.core.intent.validator import IntentValidationError
from app.core.sql.validator import SQLValidationError

from app.main import (
    intent_extractor,
    intent_validator,
    query_plan_builder,
    sql_generator,
    sql_validator,
    cache,
    metric_registry,
    database,   # REAL DB
)

router = APIRouter()
explanation_builder = ExplanationBuilder()


@router.post("/query")
def query(payload: dict):
    if "question" in payload:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Free-text questions are not accepted. "
                    "Submit structured intent JSON."
                ),
            )

    #question = payload["question"]

    try:
        #Extract + validate intent
        intent_payload = {
            "metric": "revenue",
            "version": None,
            "time_range": "last_month",
            "dimensions": [],
            "requested_filters": []
        }

        #intent = intent_extractor.extract(intent_payload)
        if "question" in payload:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Free-text questions are not accepted. "
                    "Submit structured intent JSON."
                ),
            )

        intent = intent_extractor.extract(payload)

        intent_validator.validate(intent)

        #Resolve metric + version
        metric = metric_registry.get(
            intent.metric.value,
            intent.version.value if intent.version else None,
        )
        resolved_version = metric.version

        #Build deterministic query plan (ALWAYS)
        plan = query_plan_builder.build(intent, metric)

        #Cache check
        cached = cache.get(intent, resolved_version)
        if cached is not None:
            explanation = explanation_builder.build(intent, metric, plan)
            return {
                "source": "cache",
                "result": cached,
                "explanation": explanation,
            }

        #SQL generation + validation
        sql = sql_generator.generate(plan)
        sql_validator.validate(sql)

        #REAL DB execution
        rows = database.execute(sql)

        # Analytics queries -> single scalar
        result = rows[0][0] if rows else 0

        #Cache result
        cache.set(intent, resolved_version, result)

        #Deterministic explanation
        explanation = explanation_builder.build(intent, metric, plan)

        return {
            "source": "computed",
            "sql": sql,
            "result": result,
            "explanation": explanation,
        }

    except IntentExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except IntentValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except SQLValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
