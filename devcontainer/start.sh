#! /usr/bin/env bash

cd "$(dirname -- "$0")"

podman compose -f compose.yaml up -d && \
podman compose -f compose.yaml exec kimi-agent curl -s http://thinking-tool:8080/sse > /dev/null && \
echo "✅ Network is UP" || echo "❌ Network is DOWN"

