import json
from datetime import datetime, timezone

import pytest

from adapter.parser import parse_packet  # tests parsing logic
from common.models import Track, HealthStatus  # payload types


def test_parse_single_track():
    pkt = json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(),
        "id": 1,
        "range_m": 1234.5,
        "az_deg": 10.0,
        "el_deg": 2.5,
        "vr_mps": -3.2,
        "snr_db": 20.0,
    }).encode("utf-8")

    parsed = parse_packet(pkt)

    assert parsed.kind == "track"
    assert isinstance(parsed.payload, Track)
    t = parsed.payload
    assert t.id == 1
    assert t.range_m == 1234.5


def test_parse_health_status():
    pkt = json.dumps({
        "ts": datetime.now(timezone.utc).isoformat(),
        "radar_mode": "OPERATIONAL",
        "temperature_c": 42.5,
        "supply_v": 12.2,
        "cpu_load_pct": 55.0,
    }).encode("utf-8")

    parsed = parse_packet(pkt)

    assert parsed.kind == "health"
    assert isinstance(parsed.payload, HealthStatus)
    hs = parsed.payload
    assert hs.radar_mode == "OPERATIONAL"
    assert 40.0 < hs.temperature_c < 60.0
    assert 10.0 < hs.supply_v < 13.0
    assert 0.0 <= hs.cpu_load_pct <= 100.0


def test_parse_frame_with_multiple_tracks():
    pkt = json.dumps({
        "tracks": [
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "id": 10,
                "range_m": 250.0,
                "az_deg": -5.0,
                "el_deg": 1.0,
                "vr_mps": 0.5,
                "snr_db": 15.0,
            },
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "id": 11,
                "range_m": 500.0,
                "az_deg": 12.0,
                "el_deg": 2.0,
                "vr_mps": -1.2,
                "snr_db": 30.0,
            },
        ]
    }).encode("utf-8")

    parsed = parse_packet(pkt)

    assert parsed.kind == "frame"
    payload = parsed.payload
    assert "tracks" in payload
    tracks = payload["tracks"]
    assert len(tracks) == 2
    assert all(isinstance(t, Track) for t in tracks)
    ids = {t.id for t in tracks}
    assert ids == {10, 11}


def test_parse_malformed_json_raises():
    # Missing closing brace
    pkt = b'{"id": 1, "range_m": 10.0'
    with pytest.raises(json.JSONDecodeError):
        parse_packet(pkt)