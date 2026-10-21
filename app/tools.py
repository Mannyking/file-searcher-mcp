from datetime import datetime, timezone

from mcp.server import MCPServer

from app.paths import resolve_path


def file_info(file_path: str) -> dict[str, str | int]:
    """Return a file's name, extension, size in bytes, and modification time.

    Relative paths start inside the server's project root.
    """

    path = resolve_path(value=file_path)

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


def search_files(directory: str, pattern: str) -> list[str]:
    """Recursively find files matching a glob pattern, such as '*.py'.

    Relative paths start inside the server's project root.
    """

    root = resolve_path(value=directory)

    if not root.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    return [
        str(path)
        for path in root.rglob(pattern)
        if path.is_file()
    ]


def search_text(
    directory: str,
    text: str,
    pattern: str = "*.py",
    limit: int = 50,
) -> list[dict[str, str | int]]:
    """Find literal, case-sensitive text in UTF-8 files recursively.

    Search recursively by filename pattern and return matching lines.

    Relative paths start inside the server's project root.
    """

    root = resolve_path(value=directory)

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


def read_file(
    file_path: str,
    start_line: int = 1,
    end_line: int | None = None,
) -> str:
    """Read a UTF-8 file, optionally selecting an inclusive line range.

    Line numbers start at 1. Omit end_line to read through the end.
    Returns at most 10,000 characters.

    Relative paths start inside the server's project root.
    """

    path = resolve_path(value=file_path)

    if not path.is_file():
        raise ValueError(f"Not a file: {file_path}")
    if start_line < 1:
        raise ValueError("start_line must be at least 1")
    if end_line is not None and end_line < start_line:
        raise ValueError("end_line must be at least start_line")

    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    selected: list[str] = lines[(start_line - 1):end_line]

    return "".join(selected)[:10000]


def list_directory(directory: str) -> list[dict[str, str]]:
    """List immediate directory entries with their name and types.

    Relative paths start inside the server's project root.
    """

    root = resolve_path(value=directory)

    if not root.is_dir():
        raise ValueError(f"Not a directory: {directory}")

    return [
        {
            "name": entry.name,
            "type": "directory" if entry.is_dir() else "file"
        }
        for entry in sorted(root.iterdir(), key=lambda entry: entry.name.lower())
    ]


def register(mcp: MCPServer) -> None:
    """Register the server's tools."""
    mcp.tool()(file_info)
    mcp.tool()(search_files)
    mcp.tool()(search_text)
    mcp.tool()(read_file)
    mcp.tool()(list_directory)
