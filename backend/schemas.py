from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


def _require_non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("must not be empty or whitespace-only")
    return value


class ScopeClassification(str, Enum):
    IN_SCOPE = "in_scope"
    OUT_OF_SCOPE = "out_of_scope"
    UNCLEAR = "unclear"


class ScopeAnalysisRequest(BaseModel):
    original_agreement: str = Field(
        ...,
        description="The original agreement or scope of work.",
    )
    new_client_request: str = Field(
        ...,
        description="The client's new or changed request.",
    )
    hourly_rate: float | None = Field(
        default=None,
        ge=0,
        description="Optional hourly rate used for future cost estimates.",
    )

    _validate_original_agreement = field_validator("original_agreement")(
        _require_non_blank
    )
    _validate_new_client_request = field_validator("new_client_request")(
        _require_non_blank
    )


class ExtraHoursEstimate(BaseModel):
    minimum: float | None = Field(
        default=None,
        ge=0,
        description="Estimated minimum additional hours.",
    )
    maximum: float | None = Field(
        default=None,
        ge=0,
        description="Estimated maximum additional hours.",
    )
    assumptions: list[str] = Field(
        default_factory=list,
        description="Assumptions supporting the estimate.",
    )

    @model_validator(mode="after")
    def maximum_cannot_be_less_than_minimum(self) -> "ExtraHoursEstimate":
        if (
            self.minimum is not None
            and self.maximum is not None
            and self.maximum < self.minimum
        ):
            raise ValueError("maximum extra hours must be greater than or equal to minimum")
        return self


class ScopeFinding(BaseModel):
    change_description: str = Field(
        ...,
        description="Description of the detected change.",
    )
    classification: ScopeClassification
    supporting_evidence: list[str] = Field(
        ...,
        description="Exact quotations from the supplied agreement or client request.",
        min_length=1,
    )
    explanation: str = Field(
        ...,
        description="Reasoning behind the classification.",
    )
    uncertainty: str = Field(
        ...,
        description="Known ambiguity or confidence limitation.",
    )
    estimated_extra_hours: ExtraHoursEstimate | None = None

    _validate_change_description = field_validator("change_description")(
        _require_non_blank
    )
    _validate_explanation = field_validator("explanation")(_require_non_blank)
    _validate_uncertainty = field_validator("uncertainty")(_require_non_blank)

    @field_validator("supporting_evidence")
    @classmethod
    def validate_supporting_evidence(cls, value: list[str]) -> list[str]:
        if any(not evidence.strip() for evidence in value):
            raise ValueError("supporting evidence must not contain blank items")
        return value


class ScopeAnalysisResponse(BaseModel):
    overall_summary: str = Field(
        ...,
        description="Overall summary of the scope analysis.",
    )
    suggested_client_reply: str = Field(
        ...,
        description="Professional, editable reply grounded in the supplied texts and findings.",
    )
    findings: list[ScopeFinding] = Field(
        default_factory=list,
        description="Structured changes identified in the supplied texts.",
    )
    missing_information: list[str] = Field(
        default_factory=list,
        description="Information needed to resolve uncertainty or complete the analysis.",
    )

    _validate_overall_summary = field_validator("overall_summary")(
        _require_non_blank
    )
    _validate_suggested_client_reply = field_validator("suggested_client_reply")(
        _require_non_blank
    )
