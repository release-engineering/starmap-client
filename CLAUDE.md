# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

StArMap Client is a Python client library for communicating with the StArMap service, which maps VM image builds to their cloud marketplace destinations. Part of the [release-engineering](https://github.com/release-engineering) publishing tools ecosystem.

- Python 3.10+ (tested on 3.10, 3.11, 3.12, 3.13)
- License: GPLv3+

## Development Commands

All development uses **tox**. A shared virtualenv (`{toxworkdir}/shared-environment`) is used across test environments.

```bash
# Run tests (pick a Python version)
tox -e py310

# Run a single test file
tox -e py310 -- tests/test_client.py

# Run a single test method
tox -e py310 -- tests/test_client.py::TestStarmapClient::test_query_image_success_APIv2

# Lint (flake8 + black + isort checks)
tox -e lint

# Auto-format code
tox -e autoformat

# Type checking
tox -e mypy

# Security scanning (bandit, safety, pip-audit)
tox -e security

# Build docs (output: docs/_build/html)
tox -e docs

# Regenerate pinned dependencies
tox -e pip-compile
```

## Code Style

- **Line length**: 100 characters
- **black** with `-S` (no string normalization), targeting `py310`
- **isort** with `--profile black`
- **flake8** with docstring checks (`flake8-docstrings`); D100, D104, D105 ignored globally; D101, D102, D103 ignored in tests
- **mypy** strict mode enabled
- **100% test coverage** enforced via `.coveragerc` (`fail_under = 100`)

## Architecture

### Core Modules (`starmap_client/`)

- **`client.py`** - `StarmapClient`: main API interface. Queries the StArMap server by NVR or name/version, and provides CRUD-style access to policies, mappings, and destinations. Optionally uses a local provider to cache results before falling back to the server.
- **`models.py`** - Domain models using `attrs` `@frozen` decorators for immutability. Models deserialize from JSON via `from_json()` classmethods. Key hierarchy: `Policy` -> `Mapping` -> `Destination`. Also includes `QueryResponseContainer`/`QueryResponseEntity`, `Workflow` enum, and pagination types.
- **`session.py`** - `StarmapBaseSession` (ABC), `StarmapSession` (real HTTP with retry/backoff), `StarmapMockSession` (test mock using `requests_mock`).
- **`providers/`** - Optional local data providers. `StarmapProvider` (abstract base in `base.py`), `InMemoryMapProviderV2` (in `memory.py`), and NVR parsing utilities (`utils.py`).

### Key Design Patterns

- All domain models are **immutable attrs classes** (`@frozen`). They use `StarmapJSONDecodeMixin[T]` for JSON deserialization with preprocessing, and validators from `attrs.validators` for type safety.
- The client uses an **abstract session interface** (`StarmapBaseSession`) so HTTP behavior can be swapped (real vs mock).
- The **provider pattern** allows pre-loading mappings in memory before querying the server, reducing network calls.
- API version (default `v2`) is passed through the client to construct endpoint URLs (`/api/{api_version}/*`).

### Tests (`tests/`)

- pytest with `unittest.TestCase` style classes
- JSON fixtures in `tests/data/` for API response mocking
- Provider tests in `tests/test_providers/` with their own `conftest.py`

## Dependency Management

Dependencies are managed with **pip-tools**. Unpinned deps live in `setup.py` (runtime) and `requirements-test.in` (dev). Pinned with hashes in `requirements.txt` and `requirements-test.txt`.
