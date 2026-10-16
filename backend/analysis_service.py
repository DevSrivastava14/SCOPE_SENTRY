import asyncio
import json
import logging
import os
from pathlib import Path
import time
from typing import Any

from dotenv import load_dotenv
from fastapi import HTTPException, status
from openai import APIConnectionError, APIError, APITimeoutError, OpenAI
from pydantic import ValidationError

from schemas import ScopeAnalysisRequest, ScopeAnalysisResponse

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_TIMEOUT_SECONDS = 90.0

SYSTEM_PROMPT = """You are ScopeSentry, a careful scope-analysis assistant.
Compare only the ORIGINAL AGREEMENT and NEW CLIENT REQUEST supplied by the user.
Return exactly one valid JSON object and no Markdown or other text, using this shape:
{
  "overall_summary": "string",
  "findings": [
    {
      "change_description": "string",
      "classification": "in_scope | out_of_scope | unclear",
      "supporting_evidence": ["exact quotation from the supplied texts"],
      "explanation": "string",
      "uncertainty": "string",
      "estimated_extra_hours": {
        "minimum": 0,
        "maximum": 0,
        "assumptions": ["string"]
      }
    }
  ],
  "missing_information": ["string"]
}

Every supporting_evidence item must be copied exactly from the ORIGINAL AGREEMENT
or NEW CLIENT REQUEST. Do not invent contract terms, facts, evidence, or estimates.
Use null for estimated_extra_hours when an estimate is not supported by the supplied
texts. Use "unclear" when the supplied texts do not establish the classification.
If information is missing, state that in missing_information and uncertainty.
"""


def _build_user_prompt(request: ScopeAnalysisRequest) -> str:
    return (
        "ORIGINAL AGREEMENT:\n"
        f"{request.original_agreement}\n\n"
        "NEW CLIENT REQUEST:\n"
        f"{request.new_client_request}"
    )


def _parse_response(raw_content: str, request: ScopeAnalysisRequest) -> ScopeAnalysisResponse:
    try:
        payload: Any = json.loads(raw_content)
        response = ScopeAnalysisResponse.model_validate(payload)
    except (json.JSONDecodeError, TypeError, ValidationError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned malformed scope-analysis data.",
        ) from exc

    supplied_text = (request.original_agreement, request.new_client_request)
    for finding in response.findings:
        if any(
            not any(evidence in text for text in supplied_text)
            for evidence in finding.supporting_evidence
        ):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Groq returned evidence that was not found in the supplied text.",
            )
    return response


def _call_groq(request: ScopeAnalysisRequest, api_key: str) -> str:
    client = OpenAI(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        timeout=GROQ_TIMEOUT_SECONDS,
    )
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(request)},
        ],
        temperature=0.1,
        max_tokens=2500,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("Groq returned an empty response.")
    return content


async def analyze_scope(request: ScopeAnalysisRequest) -> ScopeAnalysisResponse:
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Groq API is not configured. Set GROQ_API_KEY in backend/.env.",
        )

    request_started = time.perf_counter()
    try:
        raw_content = await asyncio.wait_for(
            asyncio.to_thread(_call_groq, request, api_key),
            timeout=GROQ_TIMEOUT_SECONDS + 5,
        )
    except (asyncio.TimeoutError, APITimeoutError) as exc:
        logger.warning(
            "Groq analysis failed after %.2f seconds with %s",
            time.perf_counter() - request_started,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="The Groq analysis request timed out.",
        ) from exc
    except (APIConnectionError, APIError, ValueError) as exc:
        logger.warning(
            "Groq analysis failed after %.2f seconds with %s",
            time.perf_counter() - request_started,
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The Groq analysis service could not complete the request.",
        ) from exc
    logger.info(
        "Groq analysis completed in %.2f seconds",
        time.perf_counter() - request_started,
    )
    return _parse_response(raw_content, request)
