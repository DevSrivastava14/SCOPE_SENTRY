import asyncio
import json
import logging

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from openai import APIConnectionError, APITimeoutError
from pydantic import ValidationError

import analysis_service
from main import app
from schemas import ScopeAnalysisRequest, ScopeAnalysisResponse


AGREEMENT = "AGREEMENT_SENTINEL: deliver the blue widget."
CLIENT_REQUEST = "REQUEST_SENTINEL: add a red widget."
API_KEY = "sentinel-api-key"


def make_request(**overrides):
    values = {
        "original_agreement": AGREEMENT,
        "new_client_request": CLIENT_REQUEST,
    }
    values.update(overrides)
    return ScopeAnalysisRequest(**values)


def make_payload(**overrides):
    payload = {
        "overall_summary": "The request changes the widget deliverable.",
        "suggested_client_reply": "Thanks for the request. Let us confirm the updated scope before proceeding.",
        "findings": [
            {
                "change_description": "Widget color change",
                "classification": "unclear",
                "supporting_evidence": [CLIENT_REQUEST],
                "explanation": "The supplied texts describe different widget colors.",
                "uncertainty": "The available agreement excerpt may not include every project detail.",
                "estimated_extra_hours": None,
            }
        ],
        "missing_information": ["Confirm the final widget color."],
    }
    payload.update(overrides)
    return payload


def response_content(**overrides):
    return json.dumps(make_payload(**overrides))


def test_valid_request_and_response_schema():
    request = make_request()
    response = ScopeAnalysisResponse.model_validate(make_payload())

    assert request.original_agreement == AGREEMENT
    assert response.suggested_client_reply.startswith("Thanks")
    assert response.findings[0].classification == "unclear"


@pytest.mark.parametrize(
    "field,value",
    [
        ("original_agreement", " "),
        ("new_client_request", "\n\t"),
    ],
)
def test_blank_request_fields_are_rejected(field, value):
    with pytest.raises(ValidationError):
        make_request(**{field: value})


def test_invalid_request_rate_is_rejected():
    with pytest.raises(ValidationError):
        make_request(hourly_rate=-1)


def test_successful_structured_response_parsing():
    response = analysis_service._parse_response(response_content(), make_request())

    assert response.overall_summary == "The request changes the widget deliverable."
    assert response.findings[0].supporting_evidence == [CLIENT_REQUEST]


def test_valid_analysis_can_return_no_findings():
    response = analysis_service._parse_response(
        response_content(findings=[], missing_information=["Confirm whether the color change is intentional."]),
        make_request(),
    )

    assert response.findings == []
    assert response.missing_information == ["Confirm whether the color change is intentional."]


def test_unclear_finding_is_preserved():
    response = analysis_service._parse_response(response_content(), make_request())

    assert response.findings[0].classification.value == "unclear"
    assert response.findings[0].uncertainty


@pytest.mark.parametrize(
    "payload",
    [
        {key: value for key, value in make_payload().items() if key != "suggested_client_reply"},
        {key: value for key, value in make_payload().items() if key != "overall_summary"},
        {**make_payload(), "findings": [{"classification": "invalid"}]},
        {**make_payload(), "suggested_client_reply": " "},
        {**make_payload(), "suggested_client_reply": None},
    ],
)
def test_missing_or_invalid_response_fields_return_malformed_error(payload):
    with pytest.raises(HTTPException) as caught:
        analysis_service._parse_response(json.dumps(payload), make_request())

    assert caught.value.status_code == 502
    assert caught.value.detail == "Groq returned malformed scope-analysis data."


@pytest.mark.parametrize("raw_content", ["not-json", "{\"overall_summary\":"])
def test_malformed_json_returns_malformed_error(raw_content):
    with pytest.raises(HTTPException) as caught:
        analysis_service._parse_response(raw_content, make_request())

    assert caught.value.status_code == 502
    assert caught.value.detail == "Groq returned malformed scope-analysis data."


def test_exact_evidence_is_accepted():
    payload = make_payload()
    payload["findings"][0]["supporting_evidence"] = [AGREEMENT]

    response = analysis_service._parse_response(json.dumps(payload), make_request())

    assert response.findings[0].supporting_evidence == [AGREEMENT]


@pytest.mark.parametrize(
    "evidence",
    [
        "The agreement says to deliver a blue widget.",
        "AGREEMENT_SENTINEL; deliver the blue widget.",
    ],
)
def test_paraphrased_or_altered_evidence_is_rejected(evidence):
    payload = make_payload()
    payload["findings"][0]["supporting_evidence"] = [evidence]

    with pytest.raises(HTTPException) as caught:
        analysis_service._parse_response(json.dumps(payload), make_request())

    assert caught.value.status_code == 502
    assert caught.value.detail == "Groq returned evidence that was not found in the supplied text."


def test_valid_shorter_evidence_substring_is_accepted():
    payload = make_payload()
    shorter_quote = "AGREEMENT_SENTINEL: deliver the blue widget"
    payload["findings"][0]["supporting_evidence"] = [shorter_quote]

    response = analysis_service._parse_response(json.dumps(payload), make_request())

    assert response.findings[0].supporting_evidence == [shorter_quote]


def test_multiline_evidence_and_long_inputs_are_validated_without_normalization():
    agreement = (
        "Long agreement header.\n"
        + ("Detailed scope line. " * 300)
        + "\nDeliverable:\tblue widget.\n"
    )
    request = make_request(original_agreement=agreement)
    multiline_quote = "Detailed scope line. Detailed scope line. \nDeliverable:\tblue widget."
    payload = make_payload()
    payload["findings"][0]["supporting_evidence"] = [multiline_quote]

    response = analysis_service._parse_response(json.dumps(payload), request)

    assert response.findings[0].supporting_evidence == [multiline_quote]


@pytest.mark.parametrize(
    "estimate",
    [
        {"minimum": -1, "maximum": 2, "assumptions": []},
        {"minimum": 4, "maximum": 2, "assumptions": ["Sentinel assumption"]},
    ],
)
def test_invalid_extra_hour_estimates_are_rejected(estimate):
    payload = make_payload()
    payload["findings"][0]["estimated_extra_hours"] = estimate

    with pytest.raises(HTTPException) as caught:
        analysis_service._parse_response(json.dumps(payload), make_request())

    assert caught.value.status_code == 502


@pytest.mark.parametrize(
    "estimate",
    [
        None,
        {"minimum": None, "maximum": None, "assumptions": ["No reliable estimate yet."]},
        {"minimum": 2, "maximum": None, "assumptions": ["Only a lower bound is known."]},
    ],
)
def test_incomplete_but_valid_extra_hour_estimates_are_preserved(estimate):
    payload = make_payload()
    payload["findings"][0]["estimated_extra_hours"] = estimate

    response = analysis_service._parse_response(json.dumps(payload), make_request())

    if estimate is None:
        assert response.findings[0].estimated_extra_hours is None
    else:
        assert response.findings[0].estimated_extra_hours.model_dump() == estimate


def test_diagnostic_logging_is_privacy_safe(caplog):
    metadata = {
        "finish_reason": "length",
        "response_characters": 8,
        "prompt_tokens": 4,
    }
    with caplog.at_level(logging.WARNING, logger="analysis_service"):
        with pytest.raises(HTTPException):
            analysis_service._parse_response("not-json", make_request(), metadata)
        with pytest.raises(HTTPException):
            analysis_service._parse_response(
                json.dumps({key: value for key, value in make_payload().items() if key != "suggested_client_reply"}),
                make_request(),
                metadata,
            )

    log_text = caplog.text
    assert "JSON decoding failed" in log_text
    assert "schema validation failed" in log_text
    assert "suggested_client_reply" in log_text
    for sensitive_value in (AGREEMENT, CLIENT_REQUEST, API_KEY, "Thanks for the request"):
        assert sensitive_value not in log_text


def test_provider_metadata_is_extracted_without_content_logging():
    response = type(
        "ProviderResponse",
        (),
        {
            "choices": [type("Choice", (), {"finish_reason": "stop"})()],
            "usage": type(
                "Usage",
                (),
                {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            )(),
        },
    )()

    metadata = analysis_service._response_metadata(response, "sentinel output")

    assert metadata == {
        "finish_reason": "stop",
        "response_characters": 15,
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30,
    }


def test_missing_api_key_returns_service_unavailable(monkeypatch):
    monkeypatch.setattr(analysis_service, "load_dotenv", lambda **kwargs: None)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(HTTPException) as caught:
        asyncio.run(analysis_service.analyze_scope(make_request()))

    assert caught.value.status_code == 503
    assert caught.value.detail == "Groq API is not configured. Set GROQ_API_KEY in backend/.env."


@pytest.mark.parametrize(
    "provider_error,expected_status,expected_detail",
    [
        (
            APITimeoutError(request=httpx.Request("POST", "https://provider.test")),
            504,
            "The Groq analysis request timed out.",
        ),
        (
            APIConnectionError(
                message="sentinel connection failure",
                request=httpx.Request("POST", "https://provider.test"),
            ),
            502,
            "The Groq analysis service could not complete the request.",
        ),
    ],
)
def test_provider_errors_are_mapped_without_network(
    monkeypatch,
    provider_error,
    expected_status,
    expected_detail,
):
    monkeypatch.setenv("GROQ_API_KEY", API_KEY)
    monkeypatch.setattr(analysis_service, "_call_groq", lambda request, api_key: (_ for _ in ()).throw(provider_error))

    with pytest.raises(HTTPException) as caught:
        asyncio.run(analysis_service.analyze_scope(make_request()))

    assert caught.value.status_code == expected_status
    assert caught.value.detail == expected_detail


def test_root_and_health_endpoints():
    with TestClient(app) as client:
        root_response = client.get("/")
        health_response = client.get("/health")

    assert root_response.status_code == 200
    assert root_response.json()["docs"] == "/docs"
    assert health_response.status_code == 200
    assert health_response.json() == {"status": "ok", "application": "ScopeSentry"}


def test_cors_allows_supported_local_frontend_and_rejects_other_origins():
    with TestClient(app) as client:
        allowed_response = client.options(
            "/analyze",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "POST",
            },
        )
        rejected_response = client.options(
            "/analyze",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "POST",
            },
        )

    assert allowed_response.status_code == 200
    assert allowed_response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert rejected_response.status_code == 400
    assert "access-control-allow-origin" not in rejected_response.headers
