import json
from typing import Optional

from pydantic import ValidationError

from .schema import Intent
from app.llm.client import LLMClient
from app.llm.prompts import INTENT_EXTRACTION_PROMPT


class IntentExtractionError(Exception):
    """Raised when intent extraction fails or is invalid."""


class IntentExtractor:
    """
    Uses an LLM strictly as an enum-mapper.
    The LLM does NOT invent semantics.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def extract(self, raw_intent: dict) -> Intent:
        """
        Accepts ONLY structured intent produced by an external adapter
        or API payload. Natural language parsing is not done here.
        """

        if raw_intent.get("status") == "UNKNOWN":
            raise IntentExtractionError(
                "Query contains concepts not supported by the intent schema"
            )

        try:
            return Intent(**raw_intent)
        except ValidationError:
            raise IntentExtractionError(
                "Intent contains unsupported enum values. "
                "The system does not infer new metrics, filters, or dimensions."
            )
