"""
Unit tests for common.models (Track and HealthStatus validation).
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from common.models import Track, HealthStatus


class TestTrack:
    """Test Track model validation."""

    def test_valid_track(self):
        """Test creating a valid Track."""
        track = Track(
            ts=datetime.now(timezone.utc),
            id=42,
            range_m=1500.0,
            az_deg=45.0,
            el_deg=10.0,
            vr_mps=-5.5,
            snr_db=25.0,
        )
        assert track.id == 42
        assert track.range_m == 1500.0
        assert track.az_deg == 45.0
        assert track.el_deg == 10.0

    def test_track_id_must_be_non_negative(self):
        """Test that Track id must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=-1,  # Invalid: negative id
                range_m=1000.0,
                az_deg=0.0,
                el_deg=5.0,
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "id" in str(exc_info.value)

    def test_track_range_must_be_non_negative(self):
        """Test that range_m must be >= 0."""
        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=1,
                range_m=-100.0,  # Invalid: negative range
                az_deg=0.0,
                el_deg=5.0,
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "range_m" in str(exc_info.value)

    def test_track_range_exceeds_max(self):
        """Test that range_m must be <= 30000."""
        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=1,
                range_m=40000.0,  # Invalid: exceeds max
                az_deg=0.0,
                el_deg=5.0,
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "range_m" in str(exc_info.value)

    def test_track_azimuth_bounds(self):
        """Test that az_deg must be in [-180, 180]."""
        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=1,
                range_m=1000.0,
                az_deg=200.0,  # Invalid: exceeds 180
                el_deg=5.0,
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "az_deg" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=1,
                range_m=1000.0,
                az_deg=-200.0,  # Invalid: less than -180
                el_deg=5.0,
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "az_deg" in str(exc_info.value)

    def test_track_elevation_bounds(self):
        """Test that el_deg must be in [-10, 90]."""
        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=1,
                range_m=1000.0,
                az_deg=0.0,
                el_deg=100.0,  # Invalid: exceeds 90
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "el_deg" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Track(
                ts=datetime.now(timezone.utc),
                id=1,
                range_m=1000.0,
                az_deg=0.0,
                el_deg=-15.0,  # Invalid: less than -10
                vr_mps=0.0,
                snr_db=20.0,
            )
        assert "el_deg" in str(exc_info.value)


class TestHealthStatus:
    """Test HealthStatus model validation."""

    def test_valid_health_status(self):
        """Test creating a valid HealthStatus."""
        health = HealthStatus(
            ts=datetime.now(timezone.utc),
            radar_mode="OPERATIONAL",
            temperature_c=45.0,
            supply_v=12.0,
            cpu_load_pct=33.5,
        )
        assert health.radar_mode == "OPERATIONAL"
        assert health.temperature_c == 45.0
        assert health.supply_v == 12.0
        assert health.cpu_load_pct == 33.5

    def test_health_status_valid_radar_modes(self):
        """Test all valid radar_mode values."""
        valid_modes = ["BOOT", "STANDBY", "OPERATIONAL", "FAULT"]
        for mode in valid_modes:
            health = HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode=mode,
                temperature_c=25.0,
                supply_v=12.0,
                cpu_load_pct=50.0,
            )
            assert health.radar_mode == mode

    def test_health_status_invalid_radar_mode(self):
        """Test that invalid radar_mode raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="INVALID_MODE",  # Invalid mode
                temperature_c=25.0,
                supply_v=12.0,
                cpu_load_pct=50.0,
            )
        assert "radar_mode" in str(exc_info.value)

    def test_health_status_temperature_bounds(self):
        """Test that temperature_c must be in [-40, 125]."""
        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="OPERATIONAL",
                temperature_c=-50.0,  # Invalid: too cold
                supply_v=12.0,
                cpu_load_pct=50.0,
            )
        assert "temperature_c" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="OPERATIONAL",
                temperature_c=150.0,  # Invalid: too hot
                supply_v=12.0,
                cpu_load_pct=50.0,
            )
        assert "temperature_c" in str(exc_info.value)

    def test_health_status_supply_voltage_bounds(self):
        """Test that supply_v must be in [9.0, 36.0]."""
        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="OPERATIONAL",
                temperature_c=25.0,
                supply_v=5.0,  # Invalid: too low
                cpu_load_pct=50.0,
            )
        assert "supply_v" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="OPERATIONAL",
                temperature_c=25.0,
                supply_v=40.0,  # Invalid: too high
                cpu_load_pct=50.0,
            )
        assert "supply_v" in str(exc_info.value)

    def test_health_status_cpu_load_bounds(self):
        """Test that cpu_load_pct must be in [0, 100]."""
        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="OPERATIONAL",
                temperature_c=25.0,
                supply_v=12.0,
                cpu_load_pct=-5.0,  # Invalid: negative
            )
        assert "cpu_load_pct" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            HealthStatus(
                ts=datetime.now(timezone.utc),
                radar_mode="OPERATIONAL",
                temperature_c=25.0,
                supply_v=12.0,
                cpu_load_pct=150.0,  # Invalid: exceeds 100
            )
        assert "cpu_load_pct" in str(exc_info.value)

    def test_health_status_boundary_values(self):
        """Test boundary values for HealthStatus fields."""
        # Min boundary
        health_min = HealthStatus(
            ts=datetime.now(timezone.utc),
            radar_mode="BOOT",
            temperature_c=-40.0,
            supply_v=9.0,
            cpu_load_pct=0.0,
        )
        assert health_min.temperature_c == -40.0
        assert health_min.supply_v == 9.0
        assert health_min.cpu_load_pct == 0.0

        # Max boundary
        health_max = HealthStatus(
            ts=datetime.now(timezone.utc),
            radar_mode="FAULT",
            temperature_c=125.0,
            supply_v=36.0,
            cpu_load_pct=100.0,
        )
        assert health_max.temperature_c == 125.0
        assert health_max.supply_v == 36.0
        assert health_max.cpu_load_pct == 100.0
