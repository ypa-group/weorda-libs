# ===== Standard Library =====
import secrets
import time
import uuid

from weorda_ids.exceptions import InvalidEntityId

_UUID7_VERSION = 7
_RFC4122_VARIANT = 0b10


def new_id() -> uuid.UUID:
    """Mint a UUIDv7 (RFC 9562): 48-bit unix-ms timestamp, then random bits.

    The only mint function on the platform (RFC-0003). Time-ordered so
    B-tree inserts stay local; otherwise indistinguishable from v4 to every
    consumer — an id's version is never inspected.
    """
    unix_ms = time.time_ns() // 1_000_000
    rand_a = secrets.randbits(12)
    rand_b = secrets.randbits(62)
    value = (
        ((unix_ms & 0xFFFF_FFFF_FFFF) << 80)
        | (_UUID7_VERSION << 76)
        | (rand_a << 64)
        | (_RFC4122_VARIANT << 62)
        | rand_b
    )
    return uuid.UUID(int=value)


def parse_id(value: str | uuid.UUID) -> uuid.UUID:
    """Parse an entity id, accepting any UUID version (legacy v4 included)."""
    if isinstance(value, uuid.UUID):
        return value
    try:
        return uuid.UUID(value)
    except (ValueError, AttributeError, TypeError) as exc:
        raise InvalidEntityId(f"not a UUID: {value!r}") from exc
