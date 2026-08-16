# ===== Standard Library =====
import uuid

from weorda_events import DomainEvent, EventBus, EventDispatcher
from sample_events import OdometerRecorded, TripFinished


class RecordingHandler:
    def __init__(self) -> None:
        self.seen: list[DomainEvent] = []

    async def handle(self, event: DomainEvent) -> None:
        self.seen.append(event)


def _odometer() -> OdometerRecorded:
    return OdometerRecorded(
        trip_id=uuid.uuid4(), vehicle_unit_id=uuid.uuid4(), kind="start", value_km=1
    )


class TestDispatcher:
    async def test_routes_by_event_type(self) -> None:
        dispatcher = EventDispatcher()
        handler = RecordingHandler()
        dispatcher.register(OdometerRecorded, handler)

        event = _odometer()
        assert await dispatcher.dispatch(event) is True
        assert handler.seen == [event]

    async def test_unhandled_type_returns_false(self) -> None:
        dispatcher = EventDispatcher()
        dispatcher.register(OdometerRecorded, RecordingHandler())
        assert await dispatcher.dispatch(TripFinished(trip_id=uuid.uuid4())) is False

    async def test_subdispatchers_compose(self) -> None:
        root, fleet_sub = EventDispatcher(), EventDispatcher()
        handler = RecordingHandler()
        fleet_sub.register(OdometerRecorded, handler)
        root.register_subdispatcher(fleet_sub)

        assert await root.dispatch(_odometer()) is True
        assert len(handler.seen) == 1
        assert root.handled_types() == frozenset({OdometerRecorded})


class TestEventBus:
    def test_collect_drains(self) -> None:
        bus = EventBus()
        first, second = _odometer(), TripFinished(trip_id=uuid.uuid4())
        bus.register_event(first)
        bus.register_event(second)

        assert bus.collect() == (first, second)
        assert len(bus) == 0
        assert bus.collect() == ()
