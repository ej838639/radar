"""
Simulate a UDP data sender for radar tracks.

Command Line:
nc -ul 9999 # netcat TCP/UDP networking utility to listen for UDP packets on 127.0.0.1 port 9999
  -u : UDP mode
  -l : listen mode
  9999 : port number

Optional other command line to pretty-print JSON data:
nc -ul 9999 | jq --unbuffered -R 'fromjson? // .'
  -R : read raw input (not JSON)
  fromjson? // . : try to parse each line as JSON, if fails output raw line
  if needed: install jq: brew install jq  (macOS) or sudo apt-get install jq (Linux)

Open another terminal and run a test: send one UDP packet with JSON data:
echo -n '{"test":1}' | nc -u -w1 127.0.0.1 9999
  -n : do not output a trailing newline
  -u : UDP mode
  -w1 : timeout after 1 second

Optional network-level debugging with tcpdump:
sudo tcpdump -i lo0 udp port 9999 -A
  -i lo0 : listen on loopback interface
  udp port 9999 : filter for UDP packets on port 9999
  -A : print each packet in ASCII

Optional process checking with lsof:
lsof -i UDP:9999
  -i UDP:9999 : list open files for UDP port 9999

Open another terminal and in the command line:
python sim_udp.py

This will start sending simulated radar track data as UDP packets to localhost:9999 at 10 Hz.

Use Ctrl+C to stop the simulator.
"""

import asyncio
import json
import random
import signal
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, confloat, conint


class Track(BaseModel):
    ts: datetime
    id: conint(ge=0)  # type: ignore
    range_m: confloat(ge=0, le=30000)  # type: ignore
    az_deg: confloat(ge=-180, le=180)  # type: ignore
    el_deg: confloat(ge=-10, le=90)  # type: ignore
    vr_mps: float
    snr_db: float


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
            # Convert to JSON and send
            json_data = json.dumps(track.model_dump(), default=str)
            self.transport.sendto(json_data.encode())
            await asyncio.sleep(1 / self.rate_hz)

    def stop(self):
        """Stop the simulator gracefully -- Called by signal handler when Ctrl+C is pressed"""
        self.running = False
        if self.transport:
            self.transport.close()


async def main():
    # Create and run simulator
    sim = UdpSimulator(rate_hz=10)

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
