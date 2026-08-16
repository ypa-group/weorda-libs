# ===== Standard Library =====
import uuid
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, kw_only=True)
class Snapshot:
    """Base for snapshot value objects (RFC-0003 reference kind: snapshot).

    A snapshot is a reference plus copied fields frozen at a business
    moment — deliberately stale. Subclasses add the copied fields;
    `captured_at` records when the business moment was.
    """

    entity_id: uuid.UUID
    captured_at: datetime
