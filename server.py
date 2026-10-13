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
def read_file(file_path: str) -> str:
    """Read a UTF-8 file and return its contents up to first 10,000 characters."""
    path = Path(file_path).expanduser().resolve()

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")

    content = path.read_text(encoding="utf-8")

    return content[:10000]


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


@mcp.prompt()
def explain_file(file_path: str) -> str:
    """Create instructions for explaining a file"""
    return (
        f"Read the file at {file_path} using the read_file tool, "
        "then explain its purpose and main components in plain language"
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
