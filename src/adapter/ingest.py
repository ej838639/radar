"""
src/ingest.py
UDP ingest module for receiving and parsing radar track data packets.
"""

import asyncio
import logging
from typing import Callable

from .parser import parse_packet, Parsed


log = logging.getLogger("ingest")
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s :: %(message)s"
)

Handler = Callable[[Parsed], None]


class UdpIngest(asyncio.DatagramProtocol):
    def __init__(self, handler: Handler):
        self.handler = handler

    def datagram_received(self, data: bytes, addr):
        asyncio.create_task(self._process(data, addr))

    async def _process(self, data: bytes, addr):
        try:
            msg = parse_packet(data)
            self.handler(msg)
        except Exception as e:
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
