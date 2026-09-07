"""Strict output contract shared by every extraction backend."""
import json
import re
from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FieldValue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    value: Annotated[str, Field(min_length=1, max_length=1024)] | None
    confidence: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]

    @field_validator("value")
    @classmethod
    def valid_text(cls, value: str | None) -> str | None:
        if value is not None and (not value.strip() or any(ord(c) < 32 for c in value)):
            raise ValueError("value must be nonempty text without control characters")
        return value


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_type: FieldValue
    issuing_country: FieldValue
    issuing_state_or_territory: FieldValue
    first_name: FieldValue
    middle_name: FieldValue
    last_name: FieldValue
    full_name: FieldValue
    date_of_birth: FieldValue
    sex: FieldValue
    nationality: FieldValue
    document_number: FieldValue
    licence_number: FieldValue
    passport_number: FieldValue
    address: FieldValue
    issue_date: FieldValue
    expiry_date: FieldValue

    @field_validator("date_of_birth", "issue_date", "expiry_date")
    @classmethod
    def valid_date(cls, field: FieldValue) -> FieldValue:
        if field.value is not None:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", field.value):
                raise ValueError("date must be ISO YYYY-MM-DD or null")
            date.fromisoformat(field.value)
        return field

    @field_validator("document_type")
    @classmethod
    def valid_document_type(cls, field: FieldValue) -> FieldValue:
        if field.value not in (None, "driver_licence", "passport"):
            raise ValueError("unsupported document type")
        return field


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def parse_result(content: str) -> ExtractionResult:
    # No fence stripping, repair, coercion, or invented defaults.
    data = json.loads(content, object_pairs_hook=_unique_object)
    return ExtractionResult.model_validate(data)
