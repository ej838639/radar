import json
from datetime import datetime, timezone

from adapter.parser import parse_packet  # tests parsing logic
from common.models import Track          # ensures the payload type

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