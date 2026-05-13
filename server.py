from __future__ import annotations

import httpx
from mcp.server.fastmcp import FastMCP

from schemas import CONVERT_CURRENCY_OUTPUT_SCHEMA, validate_schema

mcp = FastMCP(
    "Calculator MCP",
    instructions="Performs arithmetic operations and live currency conversion.",
    json_response=True,
)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Addition - add two numbers."""
    return a + b


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtraction - subtract the second number from the first."""
    return a - b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplication - multiply two given numbers."""
    return a * b


@mcp.tool()
def divide(a: float, b: float) -> float:
    """Division - divide the first number by the second."""
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b


def _normalize_currency(code: str) -> str:
    normalized = code.strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError(f"Invalid currency code: {code!r}. Use a 3-letter ISO code.")
    return normalized


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict[str, float | str]:
    """Live exchange rate calculator from one currency to another."""
    base = _normalize_currency(from_currency)
    target = _normalize_currency(to_currency)

    if amount < 0:
        raise ValueError("Amount must be greater than or equal to 0.")

    url = f"https://open.er-api.com/v6/latest/{base}"

    try:
        response = httpx.get(url, timeout=10.0)
        response.raise_for_status()
        payload = response.json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Failed to fetch live exchange rates: {exc}") from exc

    if payload.get("result") != "success":
        raise RuntimeError(f"Exchange rate provider error for base currency {base}.")

    rates = payload.get("rates", {})
    rate = rates.get(target)
    if rate is None:
        raise ValueError(f"No exchange rate available from {base} to {target}.")

    converted_amount = amount * float(rate)
    result = {
        "amount": amount,
        "from_currency": base,
        "to_currency": target,
        "rate": float(rate),
        "converted_amount": converted_amount,
    }
    validate_schema(result, CONVERT_CURRENCY_OUTPUT_SCHEMA)
    return result


if __name__ == "__main__":
    mcp.run(transport="stdio")
