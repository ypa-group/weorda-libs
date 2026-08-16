# ===== Standard Library =====
import json
from dataclasses import dataclass, field
from typing import Any

from weorda_events.domain_event import DomainEvent
from weorda_events.exceptions import EventDecodeError

_CANONICAL_KEYS = ("event_type", "event_source", "idempotency_key")


@dataclass(frozen=True, kw_only=True)
class EventAttributes:
    """The routing/dedup triple, duplicated out of the body so an operator,
    a DLQ tool, or a subscription filter can read it without decoding."""

    event_type: str
    event_source: str
    idempotency_key: str
    extra: dict[str, str] = field(default_factory=dict)

    def as_mapping(self) -> dict[str, str]:
        # Canonical triple wins over producer-supplied extras on conflict,
        # so the consumer contract stays predictable.
        merged = dict(self.extra)
        merged.update(
            event_type=self.event_type,
            event_source=self.event_source,
            idempotency_key=self.idempotency_key,
        )
        return merged


@dataclass(frozen=True, kw_only=True)
class EventMessage:
    """One publishable message: envelope body bytes + wire attributes."""

    body: bytes
    attributes: EventAttributes
    topic: str


@dataclass(frozen=True, kw_only=True)
class DecodedEnvelope:
    event_type: str
    data: dict[str, Any]


def encode_event(
    event: DomainEvent,
    *,
    event_source: str,
    extra_attributes: dict[str, str] | None = None,
) -> EventMessage:
    """Encode a domain event into the canonical envelope.

    Body is always `{"event_type": <class name>, "data": {...flat fields}}`;
    `event_source` names the producing service and comes from the publisher's
    configuration, never from the event itself.
    """
    body = json.dumps(
        {"event_type": event.event_type, "data": event.data()},
        separators=(",", ":"),
        sort_keys=True,
    ).encode()
    return EventMessage(
        body=body,
        attributes=EventAttributes(
            event_type=event.event_type,
            event_source=event_source,
            idempotency_key=event.idempotency_key,
            extra=dict(extra_attributes or {}),
        ),
        topic=type(event).topic,
    )


def decode_envelope(body: bytes | str) -> DecodedEnvelope:
    """Decode envelope bytes; raises EventDecodeError on any malformation."""
    try:
        parsed = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise EventDecodeError(f"envelope is not JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise EventDecodeError(f"envelope must be an object, got {type(parsed).__name__}")
    event_type = parsed.get("event_type")
    data = parsed.get("data")
    if not isinstance(event_type, str) or not event_type:
        raise EventDecodeError("envelope has no event_type")
    if not isinstance(data, dict):
        raise EventDecodeError("envelope has no data object")
    return DecodedEnvelope(event_type=event_type, data=data)
