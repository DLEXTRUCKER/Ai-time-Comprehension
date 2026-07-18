"""OpenAI function-tool definition and dispatcher for elapsed time."""

import json

from time_calculator import calculate_elapsed_time


ELAPSED_TIME_TOOL = {
    "type": "function",
    "name": "calculate_elapsed_time",
    "description": (
        "Calculate the exact elapsed time between an earlier message timestamp "
        "and the current message timestamp. Use this whenever elapsed time matters."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "previous_timestamp": {
                "type": "string",
                "description": "Earlier timezone-aware ISO 8601 timestamp.",
            },
            "current_timestamp": {
                "type": "string",
                "description": "Current timezone-aware ISO 8601 timestamp.",
            },
        },
        "required": ["previous_timestamp", "current_timestamp"],
        "additionalProperties": False,
    },
    "strict": True,
}


def execute_elapsed_time_tool(arguments: str) -> str:
    """Execute a model tool call and return its result as JSON."""
    values = json.loads(arguments)
    expected = {"previous_timestamp", "current_timestamp"}

    if set(values) != expected:
        raise ValueError(
            "Tool arguments must contain exactly the two timestamps."
        )

    result = calculate_elapsed_time(
        values["previous_timestamp"],
        values["current_timestamp"],
    )
    return json.dumps(result)
