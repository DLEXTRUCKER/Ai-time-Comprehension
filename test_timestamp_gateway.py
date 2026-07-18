import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from timestamp_gateway import ConversationLog


class SequenceClock:
    def __init__(self, *values: datetime) -> None:
        self.values = iter(values)

    def __call__(self) -> datetime:
        return next(self.values)


class ConversationLogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.path = Path(self.temporary_directory.name) / "conversation.jsonl"

    def test_automatically_stamps_and_stores_user_and_assistant(self) -> None:
        clock = SequenceClock(
            datetime(2026, 7, 18, 14, 0, tzinfo=timezone.utc),
            datetime(
                2026,
                7,
                18,
                8,
                0,
                5,
                tzinfo=timezone(timedelta(hours=-6)),
            ),
        )
        log = ConversationLog(self.path, clock=clock)

        user = log.record("user", "Hello")
        assistant = log.record("assistant", "Hi")

        self.assertEqual(user.timestamp, "2026-07-18T14:00:00Z")
        self.assertEqual(assistant.timestamp, "2026-07-18T14:00:05Z")
        records = [
            json.loads(line)
            for line in self.path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(
            records,
            [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2026-07-18T14:00:00Z",
                },
                {
                    "role": "assistant",
                    "content": "Hi",
                    "timestamp": "2026-07-18T14:00:05Z",
                },
            ],
        )

    def test_load_preserves_message_order_and_timestamps(self) -> None:
        log = ConversationLog(
            self.path,
            clock=SequenceClock(
                datetime(2026, 7, 18, 14, 0, tzinfo=timezone.utc),
                datetime(2026, 7, 18, 14, 1, tzinfo=timezone.utc),
            ),
        )
        log.record("user", "First")
        log.record("assistant", "Second")

        loaded = ConversationLog(self.path).load()

        self.assertEqual(
            [(message.role, message.content, message.timestamp) for message in loaded],
            [
                ("user", "First", "2026-07-18T14:00:00Z"),
                ("assistant", "Second", "2026-07-18T14:01:00Z"),
            ],
        )

    def test_renders_clear_timestamped_model_context(self) -> None:
        log = ConversationLog(
            self.path,
            clock=SequenceClock(
                datetime(2026, 7, 18, 14, 0, tzinfo=timezone.utc),
                datetime(2026, 7, 18, 14, 1, tzinfo=timezone.utc),
            ),
        )
        log.record("user", "Start the laundry.")
        log.record("assistant", "Okay.")

        self.assertEqual(
            log.render_context(),
            "[Timestamp: 2026-07-18T14:00:00Z] User: Start the laundry.\n"
            "[Timestamp: 2026-07-18T14:01:00Z] Assistant: Okay.",
        )

    def test_rejects_unsupported_role(self) -> None:
        log = ConversationLog(
            self.path,
            clock=lambda: datetime.now(timezone.utc),
        )
        with self.assertRaises(ValueError):
            log.record("system", "Not allowed")

    def test_rejects_non_string_roles_when_recording(self) -> None:
        log = ConversationLog(
            self.path,
            clock=lambda: datetime.now(timezone.utc),
        )
        invalid_roles = [[], 42]

        for role in invalid_roles:
            with self.subTest(role=role):
                with self.assertRaises(ValueError):
                    log.record(role, "Not allowed")  # type: ignore[arg-type]

    def test_loaded_non_string_roles_include_record_line_context(self) -> None:
        invalid_roles = [[], 42]

        for role in invalid_roles:
            with self.subTest(role=role):
                self.path.write_text(
                    json.dumps(
                        {
                            "role": role,
                            "content": "Not allowed",
                            "timestamp": "2026-07-18T14:00:00Z",
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )

                with self.assertRaisesRegex(
                    ValueError,
                    "Malformed conversation record on line 1",
                ):
                    ConversationLog(self.path).load()

    def test_rejects_timezone_naive_clock(self) -> None:
        log = ConversationLog(
            self.path,
            clock=lambda: datetime(2026, 7, 18, 14, 0),
        )
        with self.assertRaises(ValueError):
            log.record("user", "Hello")
        self.assertFalse(self.path.exists())

    def test_rejects_malformed_loaded_record(self) -> None:
        self.path.write_text(
            '{"role":"user","content":"Missing timestamp"}\n',
            encoding="utf-8",
        )
        with self.assertRaisesRegex(ValueError, "line 1"):
            ConversationLog(self.path).load()


if __name__ == "__main__":
    unittest.main()
