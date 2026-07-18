"""Deterministic elapsed-time calculations for language models."""

from datetime import datetime, timezone


def _parse_timestamp(value: str) -> datetime:
    """Parse an ISO 8601 timestamp and normalize it to UTC."""
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    timestamp = datetime.fromisoformat(normalized)

    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("Timestamps must include a UTC offset or end in 'Z'.")

    return timestamp.astimezone(timezone.utc)


def calculate_elapsed_time(
    previous_timestamp: str, current_timestamp: str
) -> dict[str, int]:
    """Return the exact elapsed time between two ISO 8601 timestamps."""
    previous = _parse_timestamp(previous_timestamp)
    current = _parse_timestamp(current_timestamp)
    elapsed_seconds = int((current - previous).total_seconds())

    if elapsed_seconds < 0:
        raise ValueError(
            "Current timestamp must not be earlier than previous timestamp."
        )

    days, remainder = divmod(elapsed_seconds, 86_400)
    hours, remainder = divmod(remainder, 3_600)
    minutes, seconds = divmod(remainder, 60)

    return {
        "total_seconds": elapsed_seconds,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }
