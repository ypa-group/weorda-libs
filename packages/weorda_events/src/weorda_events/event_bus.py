# ===== Standard Library =====
from weorda_events.domain_event import DomainEvent


class EventBus:
    """Request-scoped event collector.

    Use cases `register_event`; the service's middleware drains the
    collected events AFTER a 2xx response and skips them otherwise — a
    failed request publishes nothing without a try/except in any use case.
    For events another service's state depends on, use an outbox instead
    (fire-after-response can lose the event); this collector is the
    notification tier.
    """

    def __init__(self) -> None:
        self._events: list[DomainEvent] = []

    def register_event(self, event: DomainEvent) -> None:
        self._events.append(event)

    def collect(self) -> tuple[DomainEvent, ...]:
        """Return the registered events and clear the collector."""
        drained = tuple(self._events)
        self._events.clear()
        return drained

    def __len__(self) -> int:
        return len(self._events)
