# File Searcher MCP

A small, read-only MCP server for finding files, searching text, reading files,
listing directories, and inspecting file metadata. Includes prompts for explaining
files and finding implementations.

## Run

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```sh
uv run mcp run server.py
```

Runs over stdio. See [omlx.mcp.example.json](omlx.mcp.example.json) for an example
client configuration. Relative paths start at the project root; absolute paths
and `~` are also supported.

## Security

**No filesystem guardrails are currently defined.**
The server can navigate to any files and folders that the process has permission to read, including paths outside this project.

The tools are read-only, but that still carries risk: an LLM exposed to prompt
injection while browsing the internet could be manipulated into reading sensitive
local files and disclosing their contents.
