#! /usr/bin/env bash

cd "$(dirname -- "$0")"

echo "Starting containers..."
podman compose -f compose.yaml up -d --remove-orphans

echo ""
echo "Waiting for MCP gateway..."
sleep 3

# Test with PowerShell on Windows, fallback to curl
if command -v powershell.exe >/dev/null 2>&1; then
    if powershell.exe -Command "Test-NetConnection -ComputerName localhost -Port 8080 -WarningAction SilentlyContinue | Select-Object -ExpandProperty TcpTestSucceeded" 2>/dev/null | grep -q "True"; then
        echo "✅ MCP gateway is ready on http://localhost:8080"
    else
        echo "⚠️  MCP gateway may not be ready yet (port check failed)"
    fi
else
    # Unix/Mac
    if nc -z localhost 8080 2>/dev/null; then
        echo "✅ MCP gateway is ready on http://localhost:8080"
    else
        echo "⚠️  MCP gateway may not be ready yet"
    fi
fi

echo ""
echo "To use Kimi agent:"
echo "  podman compose exec -it kimi-agent kimi"
echo ""
echo "Or get a shell:"
echo "  podman compose exec -it kimi-agent bash"
echo ""
echo "To verify MCP is working inside the container:"
echo "  podman compose exec kimi-agent curl http://mcp-gateway:8080/sse"
