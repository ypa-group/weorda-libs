# weorda-events

The in-code half of the platform event contract (the wire rules live in the
vault's `event-bus-contract` note). **Stdlib only** — importable from any
service's `shared_kernel/`; enforced by this package's own test suite. The
Pub/Sub transport adapter is the separate `weorda-events-pubsub` package,
precisely so this one can stay dependency-free.

- `DomainEvent` — frozen-dataclass base. `event_type` is the class name and
  the **only** discriminator; `topic` is the logical topic (a `ClassVar`,
  resolved to a physical name by the service's settings); `idempotency_key`
  is producer-chosen and stable across retries (the natural key of the
  work, never a fresh uuid per attempt).
- `encode_event` / `decode_envelope` — the canonical envelope:
  body `{"event_type": ..., "data": {...}}`, attributes
  `{event_type, event_source, idempotency_key}` duplicated out of the body.
  The canonical triple wins over producer-supplied extras on conflict.
- `json_safe` — JSON-safe serialization for event fields (UUID, datetime,
  date, Enum, Decimal, nested dataclasses).
- `EventBus` — the request-scoped collector: use cases `register_event`,
  middleware drains after a 2xx.
- `EventDispatcher` — per-BC subdispatchers composed under a root; dispatch
  returns `False` for an unhandled type (the service acks and drops, per
  the contract's ack table).
- `EventPublisherProtocol` / `EventHandlerProtocol` — the seams transport
  adapters and handlers implement. `handle(event)` takes the event and
  nothing else — no framework types in the signature.
