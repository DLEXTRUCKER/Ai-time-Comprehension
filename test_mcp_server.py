import unittest
from unittest.mock import patch

from mcp_server import calculate_elapsed_time, mcp


class McpServerTests(unittest.IsolatedAsyncioTestCase):
    async def test_registers_calculate_elapsed_time_tool(self) -> None:
        tools = await mcp.list_tools()
        self.assertIn(
            "calculate_elapsed_time",
            [tool.name for tool in tools],
        )

    def test_returns_structured_calculator_result(self) -> None:
        result = calculate_elapsed_time(
            "2026-07-17T16:00:00-06:00",
            "2026-07-19T16:05:00-06:00",
        )
        self.assertEqual(
            result,
            {
                "total_seconds": 173100,
                "days": 2,
                "hours": 0,
                "minutes": 5,
                "seconds": 0,
            },
        )

    def test_delegates_to_time_calculator(self) -> None:
        expected = {
            "total_seconds": 60,
            "days": 0,
            "hours": 0,
            "minutes": 1,
            "seconds": 0,
        }
        with patch(
            "mcp_server._calculate_elapsed_time",
            return_value=expected,
        ) as calculator:
            result = calculate_elapsed_time("previous", "current")

        calculator.assert_called_once_with("previous", "current")
        self.assertIs(result, expected)

    def test_rejects_timestamp_without_timezone(self) -> None:
        with self.assertRaises(ValueError):
            calculate_elapsed_time(
                "2026-07-17T16:00:00",
                "2026-07-17T16:01:00Z",
            )


if __name__ == "__main__":
    unittest.main()
