import asyncio
from . import server

def main():
    """Entry point for the overseerr-mcp command.
    Properly runs the async main function from server.py
    """
    asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server']