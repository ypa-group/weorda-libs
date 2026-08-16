# ===== Standard Library =====
import dataclasses
import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any


def json_safe(value: Any) -> Any:
    """Convert an event-field value into something json.dumps accepts.

    Decimal becomes str (never float — precision is the point of Decimal);
    datetimes/dates become ISO strings; UUIDs become str; Enums their value;
    dataclasses, mappings, and sequences convert recursively.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, enum.Enum):
        return json_safe(value.value)
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: json_safe(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [json_safe(item) for item in value]
    raise TypeError(f"not JSON-safe and no conversion known: {type(value)!r}")
