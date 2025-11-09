"""
src/adapter/parser.py
Parser for incoming UDP packets into validated objects.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from common.models import BaseModel, HealthStatus, Track


class Parsed(BaseModel):
    kind: Literal["track", "health", "frame"]
    payload: Any


def parse_packet(pkt: bytes) -> Parsed:
    """
    Accepts raw UDP payload (bytes) and returns a validated Parsed object.

    Supports:
      - Single Track JSON
      - HealthStatus JSON
      - Frame JSON: {"tracks": [Track, ...]}
    """
    obj = json.loads(pkt.decode("utf-8"))

    # Frame: {"tracks": [ {...}, {...} ]}
    if isinstance(obj, dict) and "tracks" in obj and isinstance(obj["tracks"], list):
        tracks = [Track(**t) for t in obj["tracks"]]
        return Parsed(kind="frame", payload={"tracks": tracks})

    # HealthStatus: presence of required keys (heuristic)
    if isinstance(obj, dict) and {
        "radar_mode",
        "temperature_c",
        "supply_v",
        "cpu_load_pct",
    }.issubset(obj.keys()):
        hs = HealthStatus(**obj)
        return Parsed(kind="health", payload=hs)

    # Default: treat as a single Track
    return Parsed(kind="track", payload=Track(**obj))
