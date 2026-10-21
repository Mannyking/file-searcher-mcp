from mcp.server import MCPServer

from app import prompts, resources, tools

mcp = MCPServer("File Searcher")

tools.register(mcp)
resources.register(mcp)
prompts.register(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio")
