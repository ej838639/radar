"""
Main adapter adapter file

Command line:
poetry run python app.py
"""

from datetime import datetime
from pydantic import BaseModel, Field, confloat, conint
import json

class Track(BaseModel):
    ts: datetime
    id: conint(ge=0)
    range_m: confloat(ge=0, le=30000)
    az_deg: confloat(ge=-180, le=180)
    el_deg: confloat(ge=-10, le=90)
    # vr_mps: float
    # snr_db: float

class HealthStatus(BaseModel):
    ts: datetime
    radar_mode: str = Field(..., pattern="^(BOOT|STANDBY|OPERATIONAL|FAULT)$")
    temperature_c: float = Field(..., ge=-40, le=125)
    supply_v: float = Field(..., ge=9.0, le=36.0)
    cpu_load_pct: confloat(ge=0, le=100)

def main():
    tracks = list()
    tracks.append(Track(ts=datetime.utcnow(), id=0, range_m=1000, az_deg=-180, el_deg=10))
    tracks.append(Track(ts=datetime.utcnow(), id=1, range_m=1100, az_deg=-180, el_deg=10))

    print("Tracks:")
    json_str = json.dumps([t.model_dump() for t in tracks], indent=2, default=str)
    print(json_str)

if __name__ == "__main__":
    main()
