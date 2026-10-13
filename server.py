from datetime import datetime, timezone
from pathlib import Path

from mcp.server import MCPServer

mcp = MCPServer("File Searcher")


@mcp.tool()
def file_info(file_path: str) -> dict[str, str | int]:
    """Return a file's name, extension, size in bytes, and modification time."""
    path = Path(file_path).expanduser().resolve()

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    stats = path.stat()

    return {
        "name": path.name,
        "path": str(path),
        "extension": path.suffix,
        "size_bytes": stats.st_size,
        "modified_at": datetime.fromtimestamp(
            stats.st_mtime,
            tz=timezone.utc
        ).isoformat(),
    }


@mcp.tool()
def search_files(directory: str, pattern: str) -> list[str]:
    """Recursively find files matching a glob pattern, such as '*.py'."""
    root = Path(directory).expanduser().resolve()

    if not root.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    return [
        str(path)
        for path in root.rglob(pattern)
        if path.is_file()
    ]


@mcp.tool()
def search_text(
    directory: str,
    text: str,
    pattern: str = "*.py",
    limit: int = 50,
) -> list[dict[str, str | int]]:
    """Find literal, case-sensitive text in UTF-8 files recursively.

    Search recursively by filename pattern and return matching lines.
    """
    root = Path(directory).expanduser().resolve()

    if not root.is_dir():
        raise ValueError(f"Not a directory: {directory}")
    if not text:
        raise ValueError("Search text should not be empty")
    if not 1 <= limit <= 200:
        raise ValueError("Limit must be betwwen 1 and 200")

    matches = []

    for path in root.rglob(pattern=pattern):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)
        if any(part.startswith(".") for part in relative_path.parts):
            continue

        try:
            with path.open(encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    if text in line:
                        matches.append({
                            "file": relative_path.as_posix(),
                            "line": line_number,
                            "text": line.rstrip("\r\n"),
                        })

                        if len(matches) >= limit:
                            return matches
        except (UnicodeDecodeError, OSError):
            continue

    return matches


@mcp.tool()
def read_file(
    file_path: str,
    start_line: int = 1,
    end_line: int | None = None,
) -> str:
    """Read a UTF-8 file, optionally selecting an inclusive line range.

    Line numbers start at 1. Omit end_line to read through the end.
    Returns at most 10,000 characters.
    """
    path = Path(file_path).expanduser().resolve()

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    if start_line < 1:
        raise ValueError("start_line must be at least 1")
    if end_line is not None and end_line < start_line:
        raise ValueError("end_line must be at least start_line")

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    selected: list[str] = lines[(start_line - 1):end_line]

    return "".join(selected)[:10000]


@mcp.tool()
def list_directory(directory: str) -> list[dict[str, str]]:
    """List immediate directory entries with their name and types"""
    root = Path(directory).expanduser().resolve()

    if not root.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    return [
        {
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file"
        }
        for entry in sorted(root.iterdir(), key=lambda entry: entry.name.lower())
    ]


@mcp.resource("project://guide", name="Project Guide")
def project_guide() -> str:
    """Return the setup guide for this project"""

    path = Path(__file__).resolve().parent / "GUIDE.md"
    return path.read_text(encoding="utf-8")


@mcp.resource("project://overview", name="Project Overview")
def project_overview() -> str:
    """A brief description of this project."""
    return (
        "File searcher is an MCP server for finding files, searching their "
        "contents, reading text, and inspecting file metadata."
    )


@mcp.prompt()
def explain_file(file_path: str) -> str:
    """Create instructions for explaining a file"""
    return (
        f"Read the file at {file_path} using the read_file tool, "
        "then explain its purpose and main components in plain language"
    )


@mcp.prompt()
def find_implementation(topic: str, directory: str = ".") -> str:
    """Create a workflow for finding and explaining an implementation."""
    return (
        f"Find where {topic!r} is implemented in {directory!r}.\n"
        "1. Use list_directory to inspect the project structure.\n"
        "2. Use search_files to locate relevant source files.\n"
        "3. Use search_text to find relevant code and line numbers.\n"
        "4. Use file_info to check relevant files before reading them.\n"
        "5. Use read_file with line ranges to inspect matching code "
        "and its surrounding context.\n"
        "Explain what you found, citing file paths and line numbers. "
        "If you cannot find the implementation, say so."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
