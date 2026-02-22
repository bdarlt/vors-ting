# Use uv as the foundation
FROM ghcr.io/astral-sh/uv:latest AS uv

# Use Python 3.13 slim as recommended by Moonshot
FROM python:3.13-slim

# Install system dependencies (Node for Memory Bank, Go for Beads)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates nodejs npm golang-go \
    && rm -rf /var/lib/apt/lists/*

# Copy uv binaries
COPY --from=uv /uv /uvx /bin/

# 1. Install Kimi CLI
RUN uv tool install --python 3.13 kimi-cli

# 2. Install Sequential Thinking (Python-based)
RUN uv tool install mcp-sequential-thinking

# 3. Install Beads (Go-based)
RUN curl -fsSL https://raw.githubusercontent.com | bash \
    && uv tool install beads-mcp

# 4. Install Memory-Bank (Node-based)
# We use npx later to run it, but we can pre-cache it here
RUN npm install -g @alioshr/memory-bank-mcp

WORKDIR /workspace
ENV PATH="/root/.local/bin/:$PATH"

# Create the MCP config so everything is "plug-and-play"
RUN mkdir -p /root/.kimi && echo '{ \
  "mcpServers": { \
    "sequential-thinking": { \
      "command": "uvx", \
      "args": ["mcp-sequential-thinking"] \
    }, \
    "beads": { \
      "command": "uvx", \
      "args": ["beads-mcp"] \
    }, \
    "memory-bank": { \
      "command": "npx", \
      "args": ["-y", "@alioshr/memory-bank-mcp"] \
    } \
  } \
}' > /root/.kimi/mcp.json

# Launch Kimi with the pre-baked config
ENTRYPOINT ["kimi", "--mcp-config-file", "/root/.kimi/mcp.json"]

