"""
Simulate a UDP data sender for radar tracks.

"""

import asyncio
import json
import random
import signal
import os
from datetime import datetime, timezone
from typing import Optional

from common.models import HealthStatus, Track


def generate_random_track(track_id: int) -> Track:
    """Generate one random, valid radar track."""
    return Track(
        ts=datetime.now(timezone.utc),
        id=track_id,
        range_m=random.uniform(50.0, 25000.0),  # 50 m – 25 km
        az_deg=random.uniform(-60.0, 60.0),  # ±60° FOV
        el_deg=random.uniform(-5.0, 25.0),  # low elevation angles
        vr_mps=random.uniform(-50.0, 50.0),  # closing/receding rate
        snr_db=random.uniform(10.0, 40.0),  # good signal quality
    )


class UdpSimulator:
    def __init__(
        self, host: str = "127.0.0.1", port: int = 9999, rate_hz: float = 10.0
    ):
        self.host = host
        self.port = port
        self.rate_hz = rate_hz
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.running = False  # Control flag for the main loop
        self._track_id = 0

    async def start(self):
        """Start the UDP simulator"""
        loop = asyncio.get_running_loop()
        self.transport, _ = await loop.create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(), remote_addr=(self.host, self.port)
        )
        self.running = True

        while self.running:  # Loop continues until running is False
            self._track_id += 1
            track = generate_random_track(self._track_id)
            self.transport.sendto(json.dumps(track.model_dump(), default=str).encode())

            # Emit a synthetic health status every 50 tracks
            if self._track_id % 50 == 0:
                health = HealthStatus(
                    ts=datetime.now(timezone.utc),
                    radar_mode="OPERATIONAL",
                    temperature_c=random.uniform(35.0, 55.0),
                    supply_v=random.uniform(11.8, 12.6),
                    cpu_load_pct=random.uniform(5.0, 65.0),
                )
                self.transport.sendto(
                    json.dumps(health.model_dump(), default=str).encode()
                )

            await asyncio.sleep(1 / self.rate_hz)

    def stop(self):
        """Stop the simulator gracefully -- Called by signal handler when Ctrl+C is pressed"""
        self.running = False
        if self.transport:
            self.transport.close()


def test_generate_tracks():
    """Test function to generate and print random tracks."""
    tracks = [generate_random_track(i) for i in range(1, 11)]
    print("\nTracks print:")
    # Print each one nicely
    for t in tracks:
        print(
            f"ID={t.id:2d} | range={t.range_m:7.1f} m | az={t.az_deg:6.1f}° | el={t.el_deg:5.1f}° | vr={t.vr_mps:6.1f} m/s | SNR={t.snr_db:5.1f} dB"
        )

    print("\nTracks json:")
    json_str = json.dumps([t.model_dump() for t in tracks], indent=2, default=str)
    print(json_str)


async def main(
    host=os.getenv("RADAR_HOST", "127.0.0.1"),
    port=int(os.getenv("RADAR_PORT", "9999")),
    rate_hz=10,
):
    # Create and run simulator
    sim = UdpSimulator(host=host, port=port, rate_hz=rate_hz)

    # Setup signal handlers for graceful shutdown
    loop = asyncio.get_running_loop()
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        loop.add_signal_handler(
            s, sim.stop
        )  # Register stop() as the callback for SIGINT (Ctrl+C)

    try:
        await sim.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sim.stop()


if __name__ == "__main__":
    asyncio.run(main())
