#! /usr/bin/env bash

cd "$(dirname -- "$0")"

podman compose -f compose.yaml up -d && \
sleep 5 && \
podman compose -f compose.yaml exec mcp-gateway node -e "require('http').get('http://localhost:8080/sse', (r) => console.log('OK'))" && \
echo "✅ Kimi agent + sequential thinking are up" || echo "❌ MCP gateway not ready"
