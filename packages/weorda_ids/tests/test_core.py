# ===== Standard Library =====
import time
import uuid

# ===== Third-Party =====
import pytest

from weorda_ids import InvalidEntityId, new_id, parse_id


class TestNewId:
    def test_is_uuid_version_7(self) -> None:
        minted = new_id()
        assert isinstance(minted, uuid.UUID)
        assert minted.version == 7
        assert minted.variant == uuid.RFC_4122

    def test_unique_across_mints(self) -> None:
        minted = {new_id() for _ in range(10_000)}
        assert len(minted) == 10_000

    def test_time_ordered_across_millisecond_ticks(self) -> None:
        first = new_id()
        time.sleep(0.002)
        second = new_id()
        assert first < second

    def test_embeds_current_unix_millis(self) -> None:
        before_ms = time.time_ns() // 1_000_000
        minted = new_id()
        after_ms = time.time_ns() // 1_000_000
        embedded_ms = minted.int >> 80
        assert before_ms <= embedded_ms <= after_ms


class TestParseId:
    def test_accepts_uuid_instance(self) -> None:
        given = uuid.uuid4()
        assert parse_id(given) is given

    def test_accepts_v4_string(self) -> None:
        given = uuid.uuid4()
        assert parse_id(str(given)) == given

    def test_accepts_v7_string(self) -> None:
        given = new_id()
        assert parse_id(str(given)) == given

    @pytest.mark.parametrize("bad", ["", "not-a-uuid", "1234", None, 42])
    def test_rejects_non_uuid(self, bad: object) -> None:
        with pytest.raises(InvalidEntityId):
            parse_id(bad)  # type: ignore[arg-type]
