# ===== Standard Library =====
import dataclasses
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, ClassVar

from weorda_events.serialization import json_safe


@dataclass(frozen=True, kw_only=True)
class DomainEvent(ABC):
    """Base for every bus event.

    `event_type` is the class name — the ONLY discriminator on the wire
    (never add a second kind/step field for consumers to branch on).
    `topic` is the logical topic name; the service's settings resolve it to
    the physical one, and the member name must match across services for the
    same physical topic.
    """

    topic: ClassVar[str]

    @property
    def event_type(self) -> str:
        return type(self).__name__

    @property
    @abstractmethod
    def idempotency_key(self) -> str:
        """Producer-chosen, stable across the producer's retries.

        The natural key of the work (e.g. f"{trip_id}:{kind}"), never a
        fresh uuid per attempt — consumers dedupe on it.
        """

    def data(self) -> dict[str, Any]:
        """The event's fields as a flat, JSON-safe dict (the envelope's data)."""
        return {
            field.name: json_safe(getattr(self, field.name))
            for field in dataclasses.fields(self)
        }
