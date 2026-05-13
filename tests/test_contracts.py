from __future__ import annotations

from unittest.mock import Mock, patch

import httpx
import pytest

from schemas import (
    ADD_INPUT_SCHEMA,
    ADD_OUTPUT_SCHEMA,
    CONVERT_CURRENCY_INPUT_SCHEMA,
    CONVERT_CURRENCY_OUTPUT_SCHEMA,
    DIVIDE_INPUT_SCHEMA,
    DIVIDE_OUTPUT_SCHEMA,
    MULTIPLY_INPUT_SCHEMA,
    MULTIPLY_OUTPUT_SCHEMA,
    SUBTRACT_INPUT_SCHEMA,
    SUBTRACT_OUTPUT_SCHEMA,
    validate_schema,
)
from server import add, convert_currency, divide, multiply, subtract


def test_add_contract():
    payload = {"a": 3, "b": 5}
    validate_schema(payload, ADD_INPUT_SCHEMA)
    output = add(**payload)
    validate_schema(output, ADD_OUTPUT_SCHEMA)
    assert output == 8


def test_subtract_contract():
    payload = {"a": 10, "b": 4}
    validate_schema(payload, SUBTRACT_INPUT_SCHEMA)
    output = subtract(**payload)
    validate_schema(output, SUBTRACT_OUTPUT_SCHEMA)
    assert output == 6


def test_multiply_contract():
    payload = {"a": 7, "b": 6}
    validate_schema(payload, MULTIPLY_INPUT_SCHEMA)
    output = multiply(**payload)
    validate_schema(output, MULTIPLY_OUTPUT_SCHEMA)
    assert output == 42


def test_divide_contract():
    payload = {"a": 22, "b": 7}
    validate_schema(payload, DIVIDE_INPUT_SCHEMA)
    output = divide(**payload)
    validate_schema(output, DIVIDE_OUTPUT_SCHEMA)
    assert output == pytest.approx(22 / 7)


def test_divide_by_zero_fails_gracefully():
    with pytest.raises(ValueError, match="Division by zero is not allowed"):
        divide(10, 0)


def test_convert_currency_contract():
    payload = {"amount": 100.0, "from_currency": "USD", "to_currency": "EUR"}
    validate_schema(payload, CONVERT_CURRENCY_INPUT_SCHEMA)

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "result": "success",
        "rates": {"EUR": 0.9},
    }

    with patch("server.httpx.get", return_value=mock_response):
        output = convert_currency(**payload)

    validate_schema(output, CONVERT_CURRENCY_OUTPUT_SCHEMA)
    assert output["converted_amount"] == pytest.approx(90.0)


def test_convert_currency_invalid_code():
    with pytest.raises(ValueError, match="Invalid currency code"):
        convert_currency(10, "US", "EUR")


def test_convert_currency_negative_amount():
    with pytest.raises(ValueError, match="greater than or equal to 0"):
        convert_currency(-1, "USD", "EUR")


def test_convert_currency_network_failure_is_handled():
    with patch("server.httpx.get", side_effect=httpx.ReadTimeout("request timed out")):
        with pytest.raises(RuntimeError, match="Failed to fetch live exchange rates"):
            convert_currency(100, "USD", "EUR")


def test_convert_currency_provider_error_is_handled():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"result": "error"}

    with patch("server.httpx.get", return_value=mock_response):
        with pytest.raises(RuntimeError, match="Exchange rate provider error"):
            convert_currency(100, "USD", "EUR")


def test_convert_currency_missing_target_rate():
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"result": "success", "rates": {"GBP": 0.8}}

    with patch("server.httpx.get", return_value=mock_response):
        with pytest.raises(ValueError, match="No exchange rate available"):
            convert_currency(100, "USD", "EUR")
