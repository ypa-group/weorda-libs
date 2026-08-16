# ===== Standard Library =====
import json
import uuid

# ===== Third-Party =====
import pytest

from weorda_events import EventDecodeError, decode_envelope, encode_event
from sample_events import OdometerRecorded


def _event() -> OdometerRecorded:
    return OdometerRecorded(
        trip_id=uuid.UUID("018f4d2e-0000-7000-8000-000000000001"),
        vehicle_unit_id=uuid.UUID("018f4d2e-0000-7000-8000-000000000002"),
        kind="end",
        value_km=1234,
    )


class TestEncode:
    def test_body_is_canonical_envelope(self) -> None:
        message = encode_event(_event(), event_source="execution")
        body = json.loads(message.body)
        assert body["event_type"] == "OdometerRecorded"
        assert body["data"]["kind"] == "end"
        assert body["data"]["value_km"] == 1234
        assert body["data"]["trip_id"] == "018f4d2e-0000-7000-8000-000000000001"

    def test_attributes_carry_the_routing_triple(self) -> None:
        message = encode_event(_event(), event_source="execution")
        mapping = message.attributes.as_mapping()
        assert mapping["event_type"] == "OdometerRecorded"
        assert mapping["event_source"] == "execution"
        assert mapping["idempotency_key"].endswith(":end")

    def test_canonical_triple_wins_over_extras(self) -> None:
        message = encode_event(
            _event(),
            event_source="execution",
            extra_attributes={"event_type": "Spoofed", "region": "us"},
        )
        mapping = message.attributes.as_mapping()
        assert mapping["event_type"] == "OdometerRecorded"
        assert mapping["region"] == "us"

    def test_topic_comes_from_the_event_class(self) -> None:
        assert encode_event(_event(), event_source="execution").topic == (
            "weorda_shared.event_bus.topic"
        )


class TestDecode:
    def test_round_trip(self) -> None:
        message = encode_event(_event(), event_source="execution")
        decoded = decode_envelope(message.body)
        assert decoded.event_type == "OdometerRecorded"
        assert decoded.data["value_km"] == 1234

    @pytest.mark.parametrize(
        "bad",
        [
            b"not json",
            b"[]",
            b'{"data": {}}',
            b'{"event_type": ""}',
            b'{"event_type": "X"}',
            b'{"event_type": "X", "data": []}',
        ],
    )
    def test_malformed_raises_decode_error(self, bad: bytes) -> None:
        with pytest.raises(EventDecodeError):
            decode_envelope(bad)
