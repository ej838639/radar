"""
Common data models used across the application.
"""

from datetime import datetime

from pydantic import BaseModel, confloat, conint, Field


class Track(BaseModel):
    ts: datetime
    id: conint(ge=0)  # type: ignore
    range_m: confloat(ge=0, le=30000)  # type: ignore
    az_deg: confloat(ge=-180, le=180)  # type: ignore
    el_deg: confloat(ge=-10, le=90)  # type: ignore
    vr_mps: float
    snr_db: float


class HealthStatus(BaseModel):
    ts: datetime
    radar_mode: str = Field(..., pattern="^(BOOT|STANDBY|OPERATIONAL|FAULT)$")
    temperature_c: float = Field(..., ge=-40, le=125)
    supply_v: float = Field(..., ge=9.0, le=36.0)
    cpu_load_pct: confloat(ge=0, le=100)  # type: ignore