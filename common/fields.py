from datetime import UTC, datetime

from rest_framework import serializers


def iso_utc_ms(value: datetime | None) -> str | None:
    """ISO 8601, UTC, milisaniye hassasiyetli ve `Z` sonekli (§7.1)."""
    if value is None:
        return None
    return value.astimezone(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class UtcDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        return iso_utc_ms(value)
