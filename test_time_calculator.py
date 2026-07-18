import unittest

from time_calculator import calculate_elapsed_time


class CalculateElapsedTimeTests(unittest.TestCase):
    def test_eight_minutes(self) -> None:
        result = calculate_elapsed_time(
            "2026-07-17T16:00:00-06:00",
            "2026-07-17T16:08:00-06:00",
        )
        self.assertEqual(result["total_seconds"], 480)
        self.assertEqual(result["minutes"], 8)

    def test_two_days(self) -> None:
        result = calculate_elapsed_time(
            "2026-07-17T16:00:00Z",
            "2026-07-19T16:00:00Z",
        )
        self.assertEqual(result["days"], 2)

    def test_crossing_midnight(self) -> None:
        result = calculate_elapsed_time(
            "2026-07-17T23:55:00Z",
            "2026-07-18T00:10:00Z",
        )
        self.assertEqual(result["minutes"], 15)

    def test_different_offsets_same_instant(self) -> None:
        result = calculate_elapsed_time(
            "2026-07-17T16:00:00-06:00",
            "2026-07-17T15:00:00-07:00",
        )
        self.assertEqual(result["total_seconds"], 0)

    def test_daylight_saving_fallback(self) -> None:
        result = calculate_elapsed_time(
            "2026-11-01T01:30:00-06:00",
            "2026-11-01T01:30:00-07:00",
        )
        self.assertEqual(result["hours"], 1)

    def test_rejects_missing_timezone(self) -> None:
        with self.assertRaises(ValueError):
            calculate_elapsed_time(
                "2026-07-17T16:00:00",
                "2026-07-17T16:08:00Z",
            )

    def test_rejects_reversed_timestamps(self) -> None:
        with self.assertRaises(ValueError):
            calculate_elapsed_time(
                "2026-07-17T16:08:00Z",
                "2026-07-17T16:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
