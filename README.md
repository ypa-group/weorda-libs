# weorda-libs

The ecosystem-package monorepo: cross-service **contracts and plumbing**,
never business rules. Which packages exist here, what disqualifies a
candidate, and the rules each obeys are recorded in the weorda_grove vault
(`docs/reference/ecosystem-packages.md`); the identity discipline the ids
package implements is RFC-0003 (entity identity and ownership).

## Packages

| Package | Contents | Dependency weight |
| --- | --- | --- |
| `weorda-ids` | `new_id()` (UUIDv7 — the only mint on the platform), `parse_id`, `Snapshot`, `InvalidEntityId` | **stdlib only** |
| `weorda-events` | `DomainEvent`, envelope encode/decode, `EventBus`, `EventDispatcher`, handler + publisher protocols, JSON-safe serialization | **stdlib only** |
| `weorda-events-pubsub` | (next) Pub/Sub REST publisher adapter, push-envelope DTO helpers | pydantic, httpx |

`weorda-ids` and `weorda-events` are importable from a service's
`shared_kernel/` — which is why they must stay stdlib-only, and each package
enforces that in its own test suite (`test_stdlib_only.py`).

## Rules (summary — the vault note is normative)

- **Pin by commit or tag, identically across services.** A package pinned at
  HEAD is drift with extra steps.
- **Additive-only on the wire.** Envelope, attribute keys, and topic names
  change by addition + coordinated retirement, never in place.
- **No settings reads inside a package.** Values arrive as constructor
  arguments; the service's `config/` decides.
- **A package is not a place to put a decision you haven't made.**

## Development

```
uv sync
uv run pytest
```
