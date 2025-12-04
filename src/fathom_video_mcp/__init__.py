"""Fathom Video MCP Server - Access Fathom meeting recordings, summaries, and transcripts."""

__version__ = "0.1.0"

from fathom_video_mcp.server import mcp, list_meetings, get_summary, get_transcript

__all__ = ["mcp", "list_meetings", "get_summary", "get_transcript", "__version__"]
