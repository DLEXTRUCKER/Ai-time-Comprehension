"""Local MCP server exposing the deterministic elapsed-time calculator."""

from mcp.server.fastmcp import FastMCP

from time_calculator import calculate_elapsed_time as _calculate_elapsed_time


mcp = FastMCP("AI Time Comprehension")


@mcp.tool()
def calculate_elapsed_time(
    previous_timestamp: str,
    current_timestamp: str,
) -> dict[str, int]:
    """Calculate elapsed time between timezone-aware ISO 8601 timestamps."""
    return _calculate_elapsed_time(previous_timestamp, current_timestamp)


if __name__ == "__main__":
    mcp.run(transport="stdio")
