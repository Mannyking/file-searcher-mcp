from mcp.server import MCPServer
from pathlib import Path

mcp = MCPServer("File Searcher")

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


if __name__ == "__main__":
    # print(ROOT)
    mcp.run(transport="stdio")
