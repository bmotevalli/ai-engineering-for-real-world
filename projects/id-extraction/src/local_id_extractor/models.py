"""Strict output contract shared by every extraction backend."""
import json
import re
from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class FieldValue(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    value: Annotated[str, Field(min_length=1, max_length=1024)] | None
    confidence: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]

    @field_validator("value")
    @classmethod
    def valid_text(cls, value: str | None) -> str | None:
        # Newlines and tabs are meaningful in addresses and MRZ-style text. Reject
        # other control bytes, which are usually an OCR/model artifact.
        if value is not None and (not value.strip() or any(
            ord(c) < 32 and c not in "\r\n\t" for c in value
        )):
            raise ValueError("value must be nonempty text without control characters")
        return value


class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_type: FieldValue
    document_type_description: FieldValue = Field(
        default_factory=lambda: FieldValue(value=None, confidence=0.0)
    )
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

    @model_validator(mode="before")
    @classmethod
    def normalize_document_type(cls, data):
        if not isinstance(data, dict):
            return data
        field = data.get("document_type")
        if not isinstance(field, dict):
            return data
        value = field.get("value")
        aliases = {
            "driver_licence": "driver_license",
            "driver's licence": "driver_license",
            "drivers licence": "driver_license",
            "driver license": "driver_license",
            "driver's license": "driver_license",
        }
        normalized = aliases.get(value.casefold().strip(), value) if isinstance(value, str) else value
        if normalized not in (None, "driver_license", "passport", "other"):
            description = data.get("document_type_description")
            if not isinstance(description, dict) or description.get("value") in (None, ""):
                data["document_type_description"] = {
                    "value": value if isinstance(value, str) else None,
                    "confidence": field.get("confidence", 0.0),
                }
            normalized = "other"
        data["document_type"] = {**field, "value": normalized}
        return data


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
