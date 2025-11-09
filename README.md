# Radar Project

Simulated radar data pipeline with:
- Simulator that emits JSON tracks at a configurable rate
- UDP track/health/frame ingestion
- Prometheus metrics exposed at `http://localhost:8000/metrics`

## Quick Start (uv instead of pip)

Install [uv](https://github.com/astral-sh/uv) (fast Python package manager & environment tool):

```bash
brew install uv   # macOS
```

Create a virtual environment and install declared project dependencies:

```bash
uv venv .venv
uv sync            # reads pyproject.toml and creates uv.lock
```

Run the application (serves /metrics and listens for UDP):

```bash
export PYTHONPATH=src # set PYTHONPATH environment variable
cd ~/radar
uv run python -m app
```

In a second terminal start the UDP simulator:

```bash
export PYTHONPATH=src # set PYTHONPATH environment variable
cd ~/radar
uv run python -m tools.sim_udp
```

Stop with `Ctrl+C` in each terminal.

## Prometheus Server (optional)

Install Prometheus via Homebrew:

```bash
brew install prometheus
```

Use the provided `prometheus.yml` scrape config in repo root:

```bash
prometheus --config.file=./prometheus.yml --storage.tsdb.path=./.prometheus-data
```

Navigate to `http://localhost:8000/metrics` and query metrics like `radar_temperature_c`.


## Project Layout

```
src/
	app.py              # Main app: exposes metrics & ingests UDP
	adapter/            # Ingest & parse logic
	common/             # Shared models (Track, HealthStatus, etc.)
	tools/sim_udp.py    # UDP simulator
prometheus.yml        # Local Prometheus scrape config
pyproject.toml        # Project metadata & dependencies
```
