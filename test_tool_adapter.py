import json
import unittest

from tool_adapter import ELAPSED_TIME_TOOL, execute_elapsed_time_tool


class ToolAdapterTests(unittest.TestCase):
    def test_tool_definition_is_strict(self) -> None:
        self.assertEqual(ELAPSED_TIME_TOOL["type"], "function")
        self.assertEqual(
            ELAPSED_TIME_TOOL["name"],
            "calculate_elapsed_time",
        )
        self.assertTrue(ELAPSED_TIME_TOOL["strict"])
        self.assertFalse(
            ELAPSED_TIME_TOOL["parameters"]["additionalProperties"]
        )

    def test_dispatches_two_day_calculation(self) -> None:
        arguments = json.dumps(
            {
                "previous_timestamp": "2026-07-17T16:00:00Z",
                "current_timestamp": "2026-07-19T16:00:00Z",
            }
        )
        result = json.loads(execute_elapsed_time_tool(arguments))
        self.assertEqual(result["days"], 2)

    def test_rejects_extra_arguments(self) -> None:
        arguments = json.dumps(
            {
                "previous_timestamp": "2026-07-17T16:00:00Z",
                "current_timestamp": "2026-07-19T16:00:00Z",
                "untrusted_value": "ignored",
            }
        )
        with self.assertRaises(ValueError):
            execute_elapsed_time_tool(arguments)


if __name__ == "__main__":
    unittest.main()
