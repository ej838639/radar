import asyncio
import json
from datetime import datetime, timezone

import pytest

from adapter.ingest import UdpIngest
from adapter.parser import Parsed
from common.models import Track, HealthStatus


@pytest.mark.asyncio
async def test_udp_ingest_receives_and_parses_multiple_packet_kinds():
    received: list[Parsed] = []

    def handler(msg: Parsed) -> None:
        received.append(msg)

    loop = asyncio.get_running_loop()

    # Create receiving UDP endpoint on an ephemeral port (port=0)
    recv_transport, _ = await loop.create_datagram_endpoint(
        lambda: UdpIngest(handler), local_addr=("127.0.0.1", 0)
    )
    host, port = recv_transport.get_extra_info("sockname")

    # Create a sending endpoint bound to the receiver
    send_transport, _ = await loop.create_datagram_endpoint(
        lambda: asyncio.DatagramProtocol(), remote_addr=(host, port)
    )

    # Track packet
    track_pkt = json.dumps(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "id": 42,
            "range_m": 777.7,
            "az_deg": 5.0,
            "el_deg": 1.5,
            "vr_mps": -2.0,
            "snr_db": 25.0,
        }
    ).encode("utf-8")
    send_transport.sendto(track_pkt)

    # Health packet
    health_pkt = json.dumps(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "radar_mode": "OPERATIONAL",
            "temperature_c": 45.0,
            "supply_v": 12.1,
            "cpu_load_pct": 33.0,
        }
    ).encode("utf-8")
    send_transport.sendto(health_pkt)

    # Frame packet (two tracks)
    frame_pkt = json.dumps(
        {
            "tracks": [
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "id": 1,
                    "range_m": 100.0,
                    "az_deg": -3.0,
                    "el_deg": 0.5,
                    "vr_mps": 0.0,
                    "snr_db": 18.0,
                },
                {
                    "ts": datetime.now(timezone.utc).isoformat(),
                    "id": 2,
                    "range_m": 200.0,
                    "az_deg": 4.0,
                    "el_deg": 1.0,
                    "vr_mps": 1.2,
                    "snr_db": 30.0,
                },
            ]
        }
    ).encode("utf-8")
    send_transport.sendto(frame_pkt)

    # Allow async processing tasks to complete
    await asyncio.sleep(0.2)

    # Assertions
    kinds = [m.kind for m in received]
    assert "track" in kinds
    assert "health" in kinds
    assert "frame" in kinds

    # Validate payload types
    track_msgs = [m for m in received if m.kind == "track"]
    health_msgs = [m for m in received if m.kind == "health"]
    frame_msgs = [m for m in received if m.kind == "frame"]

    assert any(isinstance(m.payload, Track) for m in track_msgs)
    assert any(isinstance(m.payload, HealthStatus) for m in health_msgs)
    assert any(
        isinstance(t, Track)
        for fm in frame_msgs
        for t in fm.payload.get("tracks", [])
    )

    # Cleanup
    send_transport.close()
    recv_transport.close()