#!/bin/bash
# MCP Protocol Test - verifies server responds to MCP initialize
#
# This test sends a JSON-RPC initialize request to the MCP server via stdin
# and verifies the server returns a valid JSON-RPC response with a 'result' field.
#
# Usage: bash tests/protocol/test_mcp_protocol.sh

set -e

echo "Testing MCP protocol initialization..."

# Send initialize request and check for valid JSON-RPC response
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | \
    python -m src 2>/dev/null | \
    head -1 | \
    python -c "import sys, json; d = json.load(sys.stdin); assert 'result' in d, 'No result in response'; print('✓ MCP protocol test passed')"
