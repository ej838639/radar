# Overview
This document details the:
- Interfaces
- Message Formats

# Interfaces
## UDP Ingestion
- Protocol: UDP (IPv4/IPv6)
- Default listen: `0.0.0.0:9999`
- Message size: ≤ 1024 bytes (current simple JSON; enlarge as needed)
- Delivery semantics: Best effort (no ordering or reliability guarantees)

## Parsed Object
```sh
class Parsed(BaseModel):
    kind: Literal["track","health","frame","unknown"]
    payload: Any  # Track | HealthStatus | dict/frame
```

## Handler Contract (`handle`)
Inputs:
- msg.kind classification
- msg.payload validated by Pydantic (except frame dict list of Track)

Actions:
- Update Prometheus counters/gauges
- Log event (INFO or WARNING)

# Message Formats (JSON UTF‑8)
## Track Packet (kind inferred by shape):
```sh
{
  "ts": "2025-11-13T22:15:04.123456Z",
  "id": 137,
  "range_m": 5230.4,
  "az_deg": -12.7,
  "el_deg": 7.9,
  "vr_mps": -18.4,
  "snr_db": 26.3
}
```

## Health Packet:
```sh
{
  "ts": "2025-11-13T22:15:04.123456Z",
  "radar_mode": "OPERATIONAL",
  "temperature_c": 43.2,
  "supply_v": 12.1,
  "cpu_load_pct": 37.5
}
```

## Frame Packet (list of tracks):
```sh
{
  "ts": "2025-11-13T22:15:04.123456Z",
  "tracks": [
    {
      "ts": "2025-11-13T22:15:04.123456Z",
      "id": 201,
      "range_m": 820.1,
      "az_deg": 5.4,
      "el_deg": 2.1,
      "vr_mps": 3.0,
      "snr_db": 18.9
    }
  ]
}
```