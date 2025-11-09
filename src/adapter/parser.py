""""
src/parser.py 
Parser for incoming UDP packets into validated objects.
"""

from __future__ import annotations
import json

from typing import Literal

from common.models import Track, BaseModel

class Parsed(BaseModel):
    kind: Literal["track","health","frame"]
    payload: Track  

def parse_packet(pkt: bytes) -> Parsed:
    """
    Accepts raw UDP payload (bytes), returns a validated Parsed object.
    Supports:
      - single Track JSON

    Future extensions:
      - HealthStatus JSON
      - Frame of Tracks JSON (list of Track)
    """
    obj = json.loads(pkt.decode("utf-8"))

    return Parsed(kind="track", payload=Track(**obj))
