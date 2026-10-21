from mcp.server import MCPServer

from app.paths import resolve_path


def explain_file(file_path: str) -> str:
    """Create instructions for explaining a file.

    Relative paths start inside the server's project root.
    """

    path = resolve_path(value=file_path)

    return (
        f"Read the file at {path} using the read_file tool, "
        "then explain its purpose and main components in plain language"
    )


def find_implementation(topic: str, directory: str = ".") -> str:
    """Create a workflow for finding and explaining an implementation.

    Relative paths start inside the server's project root.
    """

    path = resolve_path(value=directory)

    return (
        f"Find where {topic!r} is implemented in {path!r}.\n"
        "1. Use list_directory to inspect the project structure.\n"
        "2. Use search_files to locate relevant source files.\n"
        "3. Use search_text to find relevant code and line numbers.\n"
        "4. Use file_info to check relevant files before reading them.\n"
        "5. Use read_file with line ranges to inspect matching code "
        "and its surrounding context.\n"
        "Explain what you found, citing file paths and line numbers. "
        "If you cannot find the implementation, say so."
    )


def register(mcp: MCPServer) -> None:
    """Register the server's prompts."""
    mcp.prompt()(explain_file)
    mcp.prompt()(find_implementation)
