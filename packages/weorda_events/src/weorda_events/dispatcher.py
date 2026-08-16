# ===== Standard Library =====
from typing import Protocol

from weorda_events.domain_event import DomainEvent


class EventHandlerProtocol(Protocol):
    """`handle(event)` takes the event and nothing else — no framework
    types in the signature (fire-and-forget is a decision for the handler's
    dependencies, not the protocol)."""

    async def handle(self, event: DomainEvent) -> None: ...


class EventDispatcher:
    """Routes decoded events to handlers by event type.

    Each bounded context owns a subdispatcher registering its own handlers
    in its own di/; the composition root builds the root dispatcher and
    composes them. `dispatch` returns False for an unhandled type — the
    service acks and drops it, per the contract's ack table; the handled
    list is derived from registrations, never a parallel list of strings.
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandlerProtocol]] = {}
        self._subdispatchers: list["EventDispatcher"] = []

    def register(
        self, event_type: type[DomainEvent], handler: EventHandlerProtocol
    ) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def register_subdispatcher(self, subdispatcher: "EventDispatcher") -> None:
        self._subdispatchers.append(subdispatcher)

    def handled_types(self) -> frozenset[type[DomainEvent]]:
        types = set(self._handlers)
        for sub in self._subdispatchers:
            types |= sub.handled_types()
        return frozenset(types)

    async def dispatch(self, event: DomainEvent) -> bool:
        """Run every handler registered for the event's type; True if any ran."""
        handled = False
        for handler in self._handlers.get(type(event), []):
            await handler.handle(event)
            handled = True
        for sub in self._subdispatchers:
            handled = await sub.dispatch(event) or handled
        return handled
