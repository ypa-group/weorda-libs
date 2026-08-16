# ===== Standard Library =====
import uuid
from dataclasses import dataclass
from typing import ClassVar

from weorda_events import DomainEvent


@dataclass(frozen=True, kw_only=True)
class OdometerRecorded(DomainEvent):
    topic: ClassVar[str] = "weorda_shared.event_bus.topic"

    trip_id: uuid.UUID
    vehicle_unit_id: uuid.UUID
    kind: str
    value_km: int

    @property
    def idempotency_key(self) -> str:
        return f"{self.trip_id}:{self.kind}"


@dataclass(frozen=True, kw_only=True)
class TripFinished(DomainEvent):
    topic: ClassVar[str] = "weorda_shared.event_bus.topic"

    trip_id: uuid.UUID

    @property
    def idempotency_key(self) -> str:
        return str(self.trip_id)
