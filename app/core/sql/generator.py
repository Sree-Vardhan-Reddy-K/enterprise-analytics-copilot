from app.core.planning.query_plan import QueryPlan
from app.llm.client import LLMClient


class SQLGenerationError(Exception):
    pass


class SQLGenerator:
    """
    Converts a QueryPlan into SQL using an LLM strictly
    as a syntax assembler.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def generate(self, plan: QueryPlan) -> str:
        prompt = self._build_prompt(plan)

        sql = self.llm.generate_sql({
        "aggregation": plan.aggregation.upper(),
        "measure_expression": plan.measure_expression,
        "fact_table": plan.fact_table,
        "joins": plan.joins,
        "time_column": plan.time_column,
        "filters": plan.filters,
        "group_by": plan.group_by,
        "time_filter": plan.time_range,
        })

        if not isinstance(sql, str) or not sql.strip():
            raise SQLGenerationError("LLM returned empty SQL")

        return sql.strip()

    #INTERNAL HELPERS

    def _render_value(self, value):
        """
        Render SQL literals correctly.
        Strings must be quoted, numbers must not.
        """
        if isinstance(value, str):
            return f"'{value}'"
        return value

    def _build_prompt(self, plan: QueryPlan) -> str:
        # Joins
        joins = "\n".join(
            f"{j.type.upper()} JOIN {j.right.split('.')[0]} ON {j.left} = {j.right}"
            for j in plan.joins
        )

        # Filters
        filters = " AND ".join(
            f"{f.column} {f.operator} {self._render_value(f.value)}"
            for f in plan.filters
        )

        filter_clause = f"\n  AND {filters}" if filters else ""

        # Group by
        group_by = ", ".join(plan.group_by) if plan.group_by else ""
        group_by_clause = f"\nGROUP BY {group_by}" if group_by else ""

        return f"""
You are a SQL formatter.

You are NOT allowed to change logic.
You MUST follow the structure below exactly.

Generate a single SELECT query.

SELECT
  {plan.aggregation.upper()}({plan.measure_expression}) AS value
FROM {plan.fact_table}
{joins}
WHERE {plan.time_column} BETWEEN <START_DATE> AND <END_DATE>{filter_clause}
{group_by_clause}
LIMIT 100;
"""
