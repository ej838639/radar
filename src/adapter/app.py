"""
Main adapter file

Command line:
python app.py
"""

import json
import random
from datetime import datetime, timezone

from pydantic import BaseModel, Field, confloat, conint



class HealthStatus(BaseModel):
    ts: datetime
    radar_mode: str = Field(..., pattern="^(BOOT|STANDBY|OPERATIONAL|FAULT)$")
    temperature_c: float = Field(..., ge=-40, le=125)
    supply_v: float = Field(..., ge=9.0, le=36.0)
    cpu_load_pct: confloat(ge=0, le=100)  # type: ignore


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


def main():
    tracks = list()
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


if __name__ == "__main__":
    main()
