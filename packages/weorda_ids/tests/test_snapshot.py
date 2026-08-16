# ===== Standard Library =====
import uuid
from dataclasses import FrozenInstanceError, dataclass
from datetime import UTC, datetime

# ===== Third-Party =====
import pytest

from weorda_ids import Snapshot


@dataclass(frozen=True, kw_only=True)
class VehicleSnapshot(Snapshot):
    registration_number: str
    seat_capacity: int


class TestSnapshot:
    def test_subclass_carries_reference_and_capture_time(self) -> None:
        vehicle_id = uuid.uuid4()
        captured = datetime.now(tz=UTC)
        snap = VehicleSnapshot(
            entity_id=vehicle_id,
            captured_at=captured,
            registration_number="AB-123",
            seat_capacity=72,
        )
        assert snap.entity_id == vehicle_id
        assert snap.captured_at == captured

    def test_immutable(self) -> None:
        snap = VehicleSnapshot(
            entity_id=uuid.uuid4(),
            captured_at=datetime.now(tz=UTC),
            registration_number="AB-123",
            seat_capacity=72,
        )
        with pytest.raises(FrozenInstanceError):
            snap.seat_capacity = 20  # type: ignore[misc]
