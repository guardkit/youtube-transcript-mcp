# Contributing

Guide for setting up a development environment, running tests, maintaining code quality, and submitting changes.

## Development Setup

### Prerequisites

- Python >= 3.10
- pip (or any PEP 517-compatible installer)
- Git

### Clone and Install

```bash
git clone https://github.com/appmilla/youtube-transcript-mcp.git
cd youtube-transcript-mcp
pip install -e ".[dev]"
```

The `[dev]` extra installs testing and linting tools: pytest, pytest-asyncio, pytest-cov, ruff, and mypy.

### Verify Installation

```bash
# Run the test suite
pytest tests/ -v

# Check the CLI works
youtube-insights-mcp cli ping
```

## Running Tests

The project uses [pytest](https://docs.pytest.org/) with [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) for async test support.

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ --cov=youtube_insights_mcp --cov-report=term
```

Target: 80% line coverage, 75% branch coverage.

### Test Markers

Custom markers are defined in `pyproject.toml`:

| Marker | Description | Usage |
|--------|-------------|-------|
| `slow` | Tests that take a long time | `pytest -m "not slow"` to skip |
| `integration` | Tests requiring network access | `pytest -m integration` to run |
| `seam` | Cross-module contract tests | `pytest -m seam` |
| `integration_contract` | Integration contract tests | `pytest -m integration_contract` |

### Configuration

Key pytest settings from `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"      # Async tests detected automatically
testpaths = ["tests"]       # Test discovery directory
```

`asyncio_mode = "auto"` means you don't need `@pytest.mark.asyncio` on every async test — pytest-asyncio handles it automatically.

## Code Quality

### Ruff (Linter + Formatter)

[Ruff](https://docs.astral.sh/ruff/) handles both linting and formatting.

```bash
# Check for issues
ruff check youtube_insights_mcp/ tests/

# Auto-fix issues
ruff check youtube_insights_mcp/ tests/ --fix

# Format code
ruff format youtube_insights_mcp/ tests/
```

Configuration from `pyproject.toml`:

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP"]
```

Enabled rule sets:

- **E** — pycodestyle errors
- **F** — pyflakes
- **W** — pycodestyle warnings
- **I** — isort (import sorting)
- **N** — pep8-naming
- **UP** — pyupgrade (modernise syntax)

### mypy (Type Checking)

[mypy](https://mypy-lang.org/) runs in strict mode for full type safety.

```bash
mypy youtube_insights_mcp/
```

Configuration from `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true
```

Third-party libraries `yt_dlp` and `youtube_transcript_api` have `ignore_missing_imports = true` overrides since they don't ship type stubs.

### Pre-Commit Checklist

Before pushing, run:

```bash
ruff check youtube_insights_mcp/ tests/
ruff format --check src/ tests/
mypy youtube_insights_mcp/
pytest tests/ -v --cov=youtube_insights_mcp
```

## Adding New Tools

MCP tools are registered at module level in `youtube_insights_mcp/__main__.py`. Follow this pattern:

### 1. Define the Tool

```python
@mcp.tool()
async def my_new_tool(
    required_param: str,
    optional_param: str = "default",
) -> dict[str, Any]:
    """Short description for Claude tool discovery.

    Detailed description of what the tool does, when to use it,
    and how results should be interpreted.

    Args:
        required_param: What this parameter controls.
        optional_param: What this controls (default: "default").

    Returns:
        Dictionary with result data or structured error.
    """
    # Convert string parameters to typed values
    # (MCP sends all parameters as strings)

    try:
        result = await some_service.process(required_param)
        return {"result": result}
    except SomeExpectedError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "DESCRIPTIVE_CODE",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.exception("Unexpected error: %s", e)
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Operation failed",
            }
        }
```

### 2. Add Service Logic (if needed)

Create or extend a service in `youtube_insights_mcp/services/`. Keep tool handlers thin — delegate business logic to services.

### 3. Add CLI Command (if applicable)

If the tool should be accessible via CLI, add a subcommand in `youtube_insights_mcp/cli.py`:

```python
# In make_parser()
my_parser = subparsers.add_parser("my-command", help="Description")
my_parser.add_argument("required_param", help="...")

# In run_command()
elif args.command == "my-command":
    from youtube_insights_mcp.services.my_service import process
    return await process(args.required_param)
```

### 4. Write Tests

Add tests in `tests/` covering:

- Happy path with valid inputs
- Error cases (invalid input, missing data)
- Edge cases (empty strings, boundary values)
- Async behaviour (cancellation handling)

### Key Rules

!!! warning "Rules for MCP Tools"
    - **Register at module level** — tools inside functions won't be discovered
    - **All logging to stderr** — never `print()` in tool handlers
    - **Parameters are strings** — convert explicitly with `int()`, `float()`, etc.
    - **Return structured errors** — use `category`/`code`/`message` format
    - **Handle CancelledError** — catch, log to stderr, and re-raise

## PR Guidelines

1. **Branch from `main`** — create a feature branch with a descriptive name
2. **Keep PRs focused** — one feature or fix per PR
3. **Include tests** — all new functionality must have test coverage
4. **Pass quality checks** — ruff, mypy, and pytest must all pass
5. **Write clear commit messages** — describe the "why", not just the "what"
6. **Update documentation** — if you add a tool or change behaviour, update the relevant docs
