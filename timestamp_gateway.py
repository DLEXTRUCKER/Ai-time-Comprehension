"""Deterministic timestamping and JSONL storage for conversation messages."""

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


Clock = Callable[[], datetime]
VALID_ROLES = {"user", "assistant"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("The clock must return a timezone-aware datetime.")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_utc_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")


@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str
    timestamp: str

    @classmethod
    def from_record(cls, record: object) -> "ConversationMessage":
        if not isinstance(record, dict) or set(record) != {
            "role",
            "content",
            "timestamp",
        }:
            raise ValueError(
                "Each record must contain role, content, and timestamp."
            )

        role = record["role"]
        content = record["content"]
        timestamp = record["timestamp"]

        if not isinstance(role, str) or role not in VALID_ROLES:
            raise ValueError("Message role must be user or assistant.")
        if not isinstance(content, str):
            raise ValueError("Message content must be a string.")
        if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
            raise ValueError("Timestamp must be a UTC ISO 8601 string ending in Z.")

        try:
            parsed = _parse_utc_timestamp(timestamp)
        except ValueError as error:
            raise ValueError("Timestamp must be valid ISO 8601.") from error
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("Timestamp must be timezone-aware.")

        return cls(role=role, content=content, timestamp=timestamp)


class ConversationLog:
    """Append-only JSONL conversation log that owns message timestamps."""

    def __init__(self, path: str | Path, clock: Clock = _utc_now) -> None:
        self.path = Path(path)
        self.clock = clock

    def record(self, role: str, content: str) -> ConversationMessage:
        if not isinstance(role, str) or role not in VALID_ROLES:
            raise ValueError("Message role must be user or assistant.")
        if not isinstance(content, str):
            raise ValueError("Message content must be a string.")

        timestamp = _format_timestamp(self.clock())
        existing_messages = self.load()
        if (
            existing_messages
            and _parse_utc_timestamp(timestamp)
            < _parse_utc_timestamp(existing_messages[-1].timestamp)
        ):
            raise ValueError(
                "The clock moved backward; refusing to append "
                "a false conversation chronology."
            )

        message = ConversationMessage(
            role=role,
            content=content,
            timestamp=timestamp,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as log_file:
            log_file.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
        return message

    def load(self) -> list[ConversationMessage]:
        if not self.path.exists():
            return []

        messages = []
        with self.path.open(encoding="utf-8") as log_file:
            for line_number, line in enumerate(log_file, start=1):
                try:
                    record = json.loads(line)
                    messages.append(ConversationMessage.from_record(record))
                except (json.JSONDecodeError, ValueError) as error:
                    raise ValueError(
                        f"Malformed conversation record on line {line_number}."
                    ) from error
        return messages

    def render_context(self) -> str:
        return "\n".join(
            f"[Timestamp: {message.timestamp}] "
            f"{message.role.capitalize()}: {message.content}"
            for message in self.load()
        )
