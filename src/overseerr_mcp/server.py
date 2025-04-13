import json
import logging
from collections.abc import Sequence
from functools import lru_cache
from typing import Any
import os
from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

load_dotenv()

from . import tools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-overseerr")

# Check for required environment variables
api_key = os.getenv("OVERSEERR_API_KEY")
url = os.getenv("OVERSEERR_URL")

if not api_key or not url:
    raise ValueError(f"OVERSEERR_API_KEY and OVERSEERR_URL environment variables are required. Working directory: {os.getcwd()}")

app = Server("mcp-overseerr")

tool_handlers = {}
def add_tool_handler(tool_class: tools.ToolHandler):
    global tool_handlers
    tool_handlers[tool_class.name] = tool_class

def get_tool_handler(name: str) -> tools.ToolHandler | None:
    if name not in tool_handlers:
        return None
    
    return tool_handlers[name]

# Register tool handlers
add_tool_handler(tools.StatusToolHandler())
add_tool_handler(tools.MovieRequestsToolHandler())
add_tool_handler(tools.TvRequestsToolHandler())

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [th.get_tool_description() for th in tool_handlers.values()]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls."""
    
    if not isinstance(arguments, dict):
        raise RuntimeError("Arguments must be a dictionary")

    tool_handler = get_tool_handler(name)
    if not tool_handler:
        raise ValueError(f"Unknown tool: {name}")

    try:
        return tool_handler.run_tool(arguments)
    except Exception as e:
        logger.error(str(e))
        raise RuntimeError(f"Caught Exception. Error: {str(e)}")

async def main():
    # Import here to avoid issues with event loops
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
