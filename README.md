# LAB 6 & LAB 9 — Tool Calling, MCP, and Regression Testing

This repository contains a complete MCP server lab project built with `FastMCP`. It implements calculator tools, a live currency conversion tool, JSON schema contracts, and an automated **regression test suite** that covers **tool calling** (as outlined in **LAB 9**): each tool is exercised with realistic payloads, inputs and outputs are checked against the same JSON schemas clients rely on, and failure paths are asserted so refactors do not silently break tool behavior.

## Lab Goals Covered

This project satisfies all requested outcomes:

- Implement an MCP server exposing 2-3 tools: **done** (exposes 5 tools)
- Define and validate JSON schemas: **done**
- Implement contract tests: **done**
- Simulate failure scenarios and handle gracefully: **done**
- **LAB 9 — Build an automated regression suite covering tool calls: done** (`pytest` in `tests/test_contracts.py`; see [Testing and regression (LAB 9)](#testing-and-regression-lab-9))

## Project Structure

- `server.py`  
  Main MCP server implementation and tool logic.
- `schemas.py`  
  JSON schema definitions and shared schema validation helper.
- `tests/test_contracts.py`  
  **LAB 9 regression suite:** contract and behavior tests for every MCP tool (happy and error paths), runnable with `pytest`.
- `tests/conftest.py`  
  Test bootstrap to ensure project imports work consistently across Windows runners and working directories.
- `calculator-mcp.json`  
  Protocol/contract document describing tools, input/output schemas, and error models.
- `claude_desktop_config.json`  
  Local MCP client config for running this server from Claude Desktop.

## Core Logic (`server.py`)

The server is created with:

- `FastMCP("Calculator MCP", ..., json_response=True)`
- Transport: `stdio` when executed directly (`python server.py`)

### Exposed MCP Tools

1. `add(a, b) -> float`  
   Returns `a + b`.

2. `subtract(a, b) -> float`  
   Returns `a - b`.

3. `multiply(a, b) -> float`  
   Returns `a * b`.

4. `divide(a, b) -> float`  
   Returns `a / b`, but raises `ValueError` when `b == 0`.

5. `convert_currency(amount, from_currency, to_currency) -> dict`  
   Fetches live FX data from `https://open.er-api.com/v6/latest/{BASE}` and returns:
   - `amount`
   - `from_currency`
   - `to_currency`
   - `rate`
   - `converted_amount`

### Validation and Guardrails in Tool Logic

- Currency code normalization via `_normalize_currency()`:
  - trims whitespace
  - uppercases values
  - enforces 3-letter alphabetic ISO-like format
- Rejects negative amounts (`amount < 0`)
- Wraps HTTP/network failures from `httpx` into `RuntimeError`
- Handles provider-level failure payloads (`result != "success"`)
- Handles missing target currency rate
- Validates final conversion payload against output schema before returning

## Schema Layer (`schemas.py`)

This module centralizes JSON schema contracts used across tests and runtime validation:

- Reusable primitives:
  - `NUMBER = {"type": "number"}`
  - `CURRENCY_CODE = {"type": "string", "pattern": "^[A-Z]{3}$"}`
- Input and output schemas for:
  - `add`
  - `subtract`
  - `multiply`
  - `divide`
  - `convert_currency`

The helper:

- `validate_schema(instance, schema)`  
  Uses `jsonschema.validate(...)` to enforce contract correctness.

## Contract File (`calculator-mcp.json`)

This file acts as a protocol-level contract definition for the MCP server:

- tool names and descriptions
- input/output schemas
- documented error models for tools with failure branches

It is useful for:

- documentation
- client generation/inspection flows
- keeping expectations explicit and reviewable

## Testing and regression (LAB 9)

**LAB 9** asks for an **automated regression suite** that covers **tool calling**. This repository delivers that as a **`pytest`** suite in `tests/test_contracts.py`:

- **Automation:** run locally or in CI with `python -m pytest` (see [How to Run](#how-to-run)); failures flag broken tools or contract drift before release.
- **Tool coverage:** every registered tool handler (`add`, `subtract`, `multiply`, `divide`, `convert_currency`) is invoked the same way the MCP layer would call into Python—using argument dicts that match each tool’s input schema—so regressions in arithmetic, currency conversion, or validation surface immediately.
- **Contract alignment:** each test validates inputs and outputs with the shared JSON schemas in `schemas.py`, keeping tests aligned with `calculator-mcp.json` and client expectations.

Tests call the **tool implementation functions** directly (not the stdio MCP wire protocol). That still constitutes regression coverage over **tool calls** in the sense LAB 9 targets: payloads, results, errors, and schemas for each tool.

## Testing Strategy (`tests/test_contracts.py`)

The suite validates both behavior and contract compliance:

### Happy-path contract tests

- Each tool receives a valid payload
- Input payload is schema-validated first
- Tool output is schema-validated second
- Functional result is asserted

### Failure-path tests (graceful handling)

- division by zero
- invalid currency code
- negative amount
- network timeout/failure from FX provider
- provider returning non-success result
- missing target conversion rate

`httpx.get(...)` is mocked for deterministic tests of currency conversion success and failure paths.

## Test Bootstrap (`tests/conftest.py`)

`conftest.py` inserts project root into `sys.path` to avoid import issues when `pytest` is run from different directories on Windows and different runner setups.

## How to Run

## 1) Create/activate virtual environment (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 2) Install dependencies

```powershell
pip install -r requirements.txt
```

## 3) Run tests

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## 4) Run MCP server

```powershell
.\.venv\Scripts\python.exe server.py
```

The server runs over `stdio`, which is the standard way MCP desktop clients connect to local tool servers.

## Claude Desktop Integration

`claude_desktop_config.json` includes an MCP server registration:

- command points to this project virtualenv Python
- argument points to `server.py`

Use that structure in your local Claude Desktop MCP config to register and launch this server.

## End-to-End Flow

1. MCP client calls tool with JSON payload
2. Tool logic executes in `server.py`
3. Validation and guard checks run
4. For currency conversion, live HTTP call retrieves rates
5. Output is returned (and conversion payload schema-validated)
6. The LAB 9 regression suite (`pytest`) guarantees both positive and negative tool-call paths stay compliant
