# weorda-ids

Entity identity per RFC-0003 (entity identity and ownership). **Stdlib
only** — importable from any service's `shared_kernel/`; the constraint is
enforced by this package's own test suite.

- `new_id()` — UUIDv7, the only mint function on the platform. The entity
  **owner** calls it in its application layer at aggregate creation (never a
  DB default), so the id exists before commit and the outbox event can carry
  it atomically.
- `parse_id(value)` — accepts any UUID version (v4 legacy ids are
  grandfathered); raises `InvalidEntityId`.
- `Snapshot` — frozen base for snapshot value objects: `entity_id` +
  `captured_at`; subclasses add the copied fields. Staleness is the point.

Typed ids are a convention, not an export: each service declares
`VehicleId = NewType("VehicleId", UUID)` in its own `shared_kernel/ids.py`
for the entities it touches, and use cases/repository protocols take the
NewType, never bare `UUID`.
