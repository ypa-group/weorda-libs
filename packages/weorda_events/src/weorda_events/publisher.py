# ===== Standard Library =====
from typing import Protocol

from weorda_events.domain_event import DomainEvent


class EventPublisherProtocol(Protocol):
    """The transport seam. Implementations live in transport packages
    (weorda-events-pubsub) or a service's shared_infrastructure — never
    here. The domain never sees a topic string or an SDK."""

    async def publish(self, event: DomainEvent) -> None: ...
