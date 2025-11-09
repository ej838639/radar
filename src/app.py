"""
app.py
Main application file

---
Optional: Test UDP Functionality with netcat (nc):

Command Line:
cd /Users/moises2020/python/radar
nc -ul 9999 # netcat TCP/UDP networking utility to listen for UDP packets on 127.0.0.1 port 9999
  -u : UDP mode
  -l : listen mode
  9999 : port number

Open another terminal and run a test: send one UDP packet with JSON data:
cd /Users/moises2020/python/radar
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

---
Test simulated UDP packets with netcat (nc):

Command Line:
cd /Users/moises2020/python/radar
nc -ul 9999 # netcat TCP/UDP networking utility to listen for UDP packets on 127.0.0.1 port 9999
  -u : UDP mode
  -l : listen mode
  9999 : port number

Open another terminal and in the command line:
cd /Users/moises2020/python/radar
PYTHONPATH=src python -m tools.sim_udp

This will start sending simulated radar track data as UDP packets to localhost:9999 at 10 Hz.
Go back to the first terminal to see the incoming UDP packets printed by netcat.

Go to second terminal and press Ctrl+C to stop the simulator.
Go to first terminal and press Ctrl+C to stop netcat.

----
Run application with Prometheus metrics (uv):

Command line:
export PYTHONPATH=src # set PYTHONPATH environment variable
cd /Users/moises2020/python/radar
uv run python -m app

Open another terminal and in the command line:
export PYTHONPATH=src # set PYTHONPATH environment variable
cd /Users/moises2020/python/radar
uv run python -m tools.sim_udp

Go back to first terminal to see application logs.
You can then access Prometheus metrics at http://localhost:8000/metrics

"""

import asyncio
import logging

from prometheus_client import Gauge, start_http_server

from adapter.ingest import run_udp_ingest
from adapter.parser import Parsed
from common.models import HealthStatus, Track

log = logging.getLogger("app")
TEMP_C = Gauge("radar_temperature_c", "Internal temperature (C)")
CPU_PCT = Gauge("radar_cpu_pct", "CPU load percent")


def handle(msg: Parsed):
    if msg.kind == "track":
        t: Track = msg.payload  # type: ignore
        log.info(
            "Track id=%s range=%.1f az=%.1f el=%.1f vr=%.1f snr=%.1f",
            t.id,
            t.range_m,
            t.az_deg,
            t.el_deg,
            t.vr_mps,
            t.snr_db,
        )
    elif msg.kind == "health":
        h: HealthStatus = msg.payload  # type: ignore
        TEMP_C.set(h.temperature_c)
        CPU_PCT.set(float(h.cpu_load_pct))
        log.info(
            "Health mode=%s temp=%.1fC cpu=%.1f%%",
            h.radar_mode,
            h.temperature_c,
            h.cpu_load_pct,
        )
    else:  # frame
        # minimal demo: count items / could route to bus, etc.
        tracks = msg.payload.get("tracks", [])  # type: ignore
        log.info("Frame received: %d tracks", len(tracks))


async def main():
    start_http_server(8000)  # /metrics
    await run_udp_ingest(handler=handle, port=9999)


if __name__ == "__main__":
    asyncio.run(main())
