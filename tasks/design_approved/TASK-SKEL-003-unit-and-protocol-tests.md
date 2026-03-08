---
complexity: 2
consumer_context:
- consumes: ping_tool
  driver: pytest-asyncio
  format_note: 'ping() is an async function returning dict with keys: status, server,
    version, timestamp'
  framework: pytest + pytest-asyncio
  task: TASK-SKEL-002
created: 2026-03-06 17:35:00+00:00
dependencies:
- TASK-SKEL-002
feature_id: FEAT-SKEL-001
id: TASK-SKEL-003
implementation_mode: task-work
parent_review: TASK-REV-87CD
priority: high
status: design_approved
tags:
- testing
- pytest
- mcp-protocol
task_type: testing
title: Add unit tests for ping tool and MCP protocol compliance test
wave: 3
---

# TASK-SKEL-003: Unit Tests + Protocol Test

## Description

Create unit tests for the `ping` tool and a protocol compliance test that verifies the MCP server responds correctly to JSON-RPC initialize requests. Tests must achieve >80% coverage of `src/`.

## Acceptance Criteria

- [ ] `tests/unit/test_ping.py` exists with at least 2 test cases
- [ ] Test: ping returns healthy status with correct fields
- [ ] Test: ping timestamp is valid UTC ISO format and recent
- [ ] `tests/protocol/test_mcp_protocol.sh` exists and is executable
- [ ] Protocol test sends JSON-RPC initialize request and verifies response
- [ ] All tests pass: `pytest tests/unit/ -v`
- [ ] Coverage >80%: `pytest tests/ --cov=src --cov-report=term`
- [ ] Protocol test passes: `bash tests/protocol/test_mcp_protocol.sh`

## Implementation Notes

Refer to the feature spec for exact test implementations:
- Unit tests: [FEAT-SKEL-001 Unit Test](../../../docs/features/FEAT-SKEL-001-basic-mcp-server.md#unit-test-testsunittest_pingpy)
- Protocol test: [FEAT-SKEL-001 Protocol Test](../../../docs/features/FEAT-SKEL-001-basic-mcp-server.md#protocol-test-testsprotocoltest_mcp_protocolsh)

Key patterns:
- Use `@pytest.mark.asyncio` for async test functions
- Import ping directly: `from src.__main__ import ping`
- Protocol test sends JSON-RPC via stdin pipe to `python -m src`

## Seam Tests

The following seam test validates the integration contract with the producer task. Implement this test to verify the boundary before integration.

```python
"""Seam test: verify ping_tool contract from TASK-SKEL-002."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("ping_tool")
def test_ping_tool_format():
    """Verify ping_tool matches the expected format.

    Contract: ping() returns dict with keys: status, server, version, timestamp
    Producer: TASK-SKEL-002
    """
    import asyncio
    from src.__main__ import ping

    result = asyncio.run(ping())

    assert isinstance(result, dict), "ping must return a dict"
    assert "status" in result, "ping must include 'status' key"
    assert "server" in result, "ping must include 'server' key"
    assert "version" in result, "ping must include 'version' key"
    assert "timestamp" in result, "ping must include 'timestamp' key"
```