from __future__ import annotations

from jsonschema import validate


NUMBER = {"type": "number"}
CURRENCY_CODE = {"type": "string", "pattern": "^[A-Z]{3}$"}


ADD_INPUT_SCHEMA = {
    "type": "object",
    "properties": {"a": NUMBER, "b": NUMBER},
    "required": ["a", "b"],
    "additionalProperties": False,
}

ADD_OUTPUT_SCHEMA = NUMBER

SUBTRACT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {"a": NUMBER, "b": NUMBER},
    "required": ["a", "b"],
    "additionalProperties": False,
}

SUBTRACT_OUTPUT_SCHEMA = NUMBER

MULTIPLY_INPUT_SCHEMA = {
    "type": "object",
    "properties": {"a": NUMBER, "b": NUMBER},
    "required": ["a", "b"],
    "additionalProperties": False,
}

MULTIPLY_OUTPUT_SCHEMA = NUMBER

DIVIDE_INPUT_SCHEMA = {
    "type": "object",
    "properties": {"a": NUMBER, "b": NUMBER},
    "required": ["a", "b"],
    "additionalProperties": False,
}

DIVIDE_OUTPUT_SCHEMA = NUMBER

CONVERT_CURRENCY_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {"type": "number", "minimum": 0},
        "from_currency": CURRENCY_CODE,
        "to_currency": CURRENCY_CODE,
    },
    "required": ["amount", "from_currency", "to_currency"],
    "additionalProperties": False,
}

CONVERT_CURRENCY_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {"type": "number", "minimum": 0},
        "from_currency": CURRENCY_CODE,
        "to_currency": CURRENCY_CODE,
        "rate": {"type": "number", "minimum": 0},
        "converted_amount": {"type": "number", "minimum": 0},
    },
    "required": ["amount", "from_currency", "to_currency", "rate", "converted_amount"],
    "additionalProperties": False,
}


def validate_schema(instance: object, schema: dict) -> None:
    """Validate an instance against a JSON schema."""
    validate(instance=instance, schema=schema)
