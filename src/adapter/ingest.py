"""
src/ingest.py
UDP ingest module for receiving and parsing radar track data packets.
"""

import asyncio # type: ignore
import logging # type: ignore
from typing import Callable # type: ignore

from prometheus_client import Counter # type: ignore

from .parser import parse_packet, Parsed # type: ignore


log = logging.getLogger("ingest")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s :: %(message)s"
)

Handler = Callable[[Parsed], None]

# Prometheus counters for ingest path
INGEST_PACKETS_TOTAL = Counter(
    "radar_ingest_packets_total", "Total UDP datagrams received"
)
PARSE_ERRORS_TOTAL = Counter(
    "radar_parse_errors_total", "Total UDP datagrams that failed to parse"
)


class UdpIngest(asyncio.DatagramProtocol):
    def __init__(self, handler: Handler):
        self.handler = handler

    def datagram_received(self, data: bytes, addr):
        # Count every datagram as soon as it arrives
        INGEST_PACKETS_TOTAL.inc()
        asyncio.create_task(self._process(data, addr))

    async def _process(self, data: bytes, addr):
        try:
            msg = parse_packet(data)
            self.handler(msg)
        except Exception as e:
            PARSE_ERRORS_TOTAL.inc()
            log.error("parse error from %s: %s", addr, e)


async def run_udp_ingest(handler: Handler, host: str = "0.0.0.0", port: int = 9999):
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: UdpIngest(handler), local_addr=(host, port)
    )
    log.info("UDP ingest listening on %s:%d", host, port)
    try:
        while True:
            await asyncio.sleep(3600)
    finally:
        transport.close()
