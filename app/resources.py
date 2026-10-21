from mcp.server import MCPServer

from app.paths import ROOT


def project_guide() -> str:
    """Return the setup guide for this project"""

    path = ROOT / "GUIDE.md"
    return path.read_text(encoding="utf-8")


def project_overview() -> str:
    """A brief description of this project."""

    return (
        "File searcher is an MCP server for finding files, searching their "
        "contents, reading text, and inspecting file metadata."
    )


def register(mcp: MCPServer) -> None:
    """Register the server's resources."""
    mcp.resource("project://guide", name="Project Guide")(project_guide)
    mcp.resource("project://overview", name="Project Overview")(project_overview)
