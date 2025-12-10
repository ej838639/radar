"""
Integration tests for Prometheus metrics in the radar application.
"""

import asyncio
import json
from datetime import datetime, timezone

import pytest
from prometheus_client import REGISTRY

from adapter.ingest import UdpIngest
from adapter.parser import Parsed
from app import handle, TEMP_C, CPU_PCT, PKTS_TOTAL
from common.models import Track, HealthStatus


class TestMetricsHandler:
    """Test that the handle() function updates Prometheus metrics correctly."""

    def setup_method(self):
        """Reset metrics before each test."""
        # Clear all collectors to reset metrics
        PKTS_TOTAL.labels(kind="track")._value._value = 0
        PKTS_TOTAL.labels(kind="health")._value._value = 0
        PKTS_TOTAL.labels(kind="frame")._value._value = 0
        PKTS_TOTAL.labels(kind="unknown")._value._value = 0
        TEMP_C.set(0)
        CPU_PCT.set(0)

    def test_handle_track_increments_counter(self):
        """Test that handling a track message increments the track counter."""
        track = Track(
            ts=datetime.now(timezone.utc),
            id=1,
            range_m=1000.0,
            az_deg=45.0,
            el_deg=10.0,
            vr_mps=-5.0,
            snr_db=25.0,
        )
        msg = Parsed(kind="track", payload=track)

        initial = PKTS_TOTAL.labels(kind="track")._value._value
        handle(msg)
        final = PKTS_TOTAL.labels(kind="track")._value._value

        assert final == initial + 1

    def test_handle_health_updates_gauges(self):
        """Test that handling a health message updates temperature and CPU gauges."""
        health = HealthStatus(
            ts=datetime.now(timezone.utc),
            radar_mode="OPERATIONAL",
            temperature_c=42.5,
            supply_v=12.0,
            cpu_load_pct=65.3,
        )
        msg = Parsed(kind="health", payload=health)

        handle(msg)

        assert TEMP_C._value._value == 42.5
        assert CPU_PCT._value._value == 65.3
        assert PKTS_TOTAL.labels(kind="health")._value._value >= 1

    def test_handle_frame_increments_counter(self):
        """Test that handling a frame message increments the frame counter."""
        frame_payload = {
            "tracks": [
                Track(
                    ts=datetime.now(timezone.utc),
                    id=1,
                    range_m=100.0,
                    az_deg=0.0,
                    el_deg=5.0,
                    vr_mps=0.0,
                    snr_db=20.0,
                ),
                Track(
                    ts=datetime.now(timezone.utc),
                    id=2,
                    range_m=200.0,
                    az_deg=10.0,
                    el_deg=3.0,
                    vr_mps=1.5,
                    snr_db=30.0,
                ),
            ]
        }
        msg = Parsed(kind="frame", payload=frame_payload)

        initial = PKTS_TOTAL.labels(kind="frame")._value._value
        handle(msg)
        final = PKTS_TOTAL.labels(kind="frame")._value._value

        assert final == initial + 1

    def test_handle_multiple_tracks_accumulates_counter(self):
        """Test that multiple track messages accumulate the counter."""
        track1 = Track(
            ts=datetime.now(timezone.utc),
            id=1,
            range_m=500.0,
            az_deg=0.0,
            el_deg=5.0,
            vr_mps=0.0,
            snr_db=15.0,
        )
        track2 = Track(
            ts=datetime.now(timezone.utc),
            id=2,
            range_m=1500.0,
            az_deg=90.0,
            el_deg=8.0,
            vr_mps=-2.0,
            snr_db=22.0,
        )

        initial = PKTS_TOTAL.labels(kind="track")._value._value
        handle(Parsed(kind="track", payload=track1))
        handle(Parsed(kind="track", payload=track2))
        final = PKTS_TOTAL.labels(kind="track")._value._value

        assert final == initial + 2

    def test_handle_multiple_health_updates_latest_gauge_value(self):
        """Test that multiple health messages update gauges to the latest value."""
        health1 = HealthStatus(
            ts=datetime.now(timezone.utc),
            radar_mode="BOOT",
            temperature_c=30.0,
            supply_v=12.0,
            cpu_load_pct=40.0,
        )
        health2 = HealthStatus(
            ts=datetime.now(timezone.utc),
            radar_mode="OPERATIONAL",
            temperature_c=55.0,
            supply_v=12.5,
            cpu_load_pct=75.0,
        )

        handle(Parsed(kind="health", payload=health1))
        assert TEMP_C._value._value == 30.0
        assert CPU_PCT._value._value == 40.0

        handle(Parsed(kind="health", payload=health2))
        assert TEMP_C._value._value == 55.0
        assert CPU_PCT._value._value == 75.0


@pytest.mark.asyncio
async def test_metrics_integration_with_udp_ingest():
    """Integration test: send UDP packets and verify metrics are updated."""
    received_messages = []

    def test_handler(msg: Parsed) -> None:
        received_messages.append(msg)
        handle(msg)  # Also update metrics

    loop = asyncio.get_running_loop()

    # Create receiving UDP endpoint
    recv_transport, _ = await loop.create_datagram_endpoint(
        lambda: UdpIngest(test_handler), local_addr=("127.0.0.1", 0)
    )
    host, port = recv_transport.get_extra_info("sockname")

    # Create sending endpoint
    send_transport, _ = await loop.create_datagram_endpoint(
        lambda: asyncio.DatagramProtocol(), remote_addr=(host, port)
    )

    # Reset metrics
    initial_track_count = PKTS_TOTAL.labels(kind="track")._value._value

    # Send a track packet
    track_pkt = json.dumps(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "id": 99,
            "range_m": 2500.0,
            "az_deg": 30.0,
            "el_deg": 15.0,
            "vr_mps": -4.0,
            "snr_db": 28.0,
        }
    ).encode("utf-8")
    send_transport.sendto(track_pkt)

    # Send a health packet
    health_pkt = json.dumps(
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "radar_mode": "OPERATIONAL",
            "temperature_c": 48.5,
            "supply_v": 12.2,
            "cpu_load_pct": 62.0,
        }
    ).encode("utf-8")
    send_transport.sendto(health_pkt)

    # Allow async processing
    await asyncio.sleep(0.4)

    # Verify metrics
    final_track_count = PKTS_TOTAL.labels(kind="track")._value._value
    assert final_track_count > initial_track_count

    assert TEMP_C._value._value == 48.5
    assert CPU_PCT._value._value == 62.0

    # Verify messages were received
    assert len(received_messages) >= 2
    kinds = [m.kind for m in received_messages]
    assert "track" in kinds
    assert "health" in kinds

    # Cleanup
    send_transport.close()
    recv_transport.close()
