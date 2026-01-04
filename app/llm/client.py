from typing import Dict, Any


class LLMClient:
    """
    Contract-driven mock LLM.

    IMPORTANT DESIGN CHOICE:
    ------------------------
    This client does NOT:
    - parse natural language
    - guess intent
    - infer business semantics
    - decide metrics, filters, joins, or grain

    Those responsibilities live OUTSIDE this class.

    This client ONLY:
    1) Accepts already-structured intent (or UNKNOWN)
    2) Assembles SQL syntax from a validated QueryPlan
    """

    # Intent handling
    def handle_intent(self, intent_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Accepts ONLY:
        - a fully structured intent dict (already validated), OR
        - {"status": "UNKNOWN"}

        Any attempt to pass free-form text here is a usage error.
        """

        if not isinstance(intent_payload, dict):
            raise RuntimeError(
                "LLMClient.handle_intent expects structured intent dict only"
            )

        if intent_payload.get("status") == "UNKNOWN":
            return intent_payload

        #here intent is assumed to be validated
        return intent_payload

    # SQL generation (syntax-only responsibility)    
    def generate_sql(self, plan: dict) -> str:
        """
        Generate SQL strictly from a QueryPlan.

        The QueryPlan is assumed to be:
        - semantically valid
        - business-rule compliant
        - already validated elsewhere

        This method does NOT:
        - change logic
        - add filters
        - remove joins
        - reinterpret meaning
        """
        joins = "\n".join(
            f"{j.type.upper()} JOIN {j.right.split('.')[0]} ON {j.left} = {j.right}"
            for j in plan["joins"]
        )

        filters = " AND ".join(
            f"{f.column} {f.operator} '{f.value}'"
            for f in plan["filters"]
        )

        group_by = (
            f"\nGROUP BY {', '.join(plan['group_by'])}"
            if plan["group_by"]
            else ""
        )

        return f"""
    SELECT
    {plan['aggregation']}({plan['measure_expression']}) AS value
    FROM {plan['fact_table']}
    {joins}
    WHERE {plan['time_column']} BETWEEN '2024-01-01' AND '2024-01-31'
    AND {filters}
    {group_by}
    LIMIT 100
    """.strip()
