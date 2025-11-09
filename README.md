# Radar Project

Simulated radar data pipeline with:
- UDP track/health/frame ingestion on port 9999
- Prometheus metrics exposed at `http://localhost:8000/metrics`
- Simulator that emits JSON tracks at a configurable rate

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
uv run PYTHONPATH=src python -m app
```

In a second terminal start the UDP simulator:

```bash
uv run PYTHONPATH=src python -m tools.sim_udp
```

Watch incoming packets with netcat:

```bash
nc -ul 9999
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

Navigate to `http://localhost:9090` and query metrics like `radar_temperature_c`.

## Adding / Removing Dependencies

Add a runtime dependency:

```bash
uv add rich
```

Add a dev dependency:

```bash
uv add --group dev pytest
```

Remove a dependency:

```bash
uv remove rich
```

Re-sync after manual `pyproject.toml` edits:

```bash
uv sync
```

## Verifying Install

```bash
uv run python -c "import prometheus_client, pydantic; print('prometheus_client', prometheus_client.__version__); print('pydantic', pydantic.__version__)"
```

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

## Running Tests (if/when added)

```bash
uv run pytest -q
```

## Typical Workflow

1. `uv sync` (first time or after dependency changes)
2. Start app: `uv run PYTHONPATH=src python -m app`
3. Start simulator: `uv run PYTHONPATH=src python -m tools.sim_udp`
4. (Optional) Start Prometheus server
5. Inspect metrics / logs

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| ModuleNotFoundError (prometheus_client) | Env not synced | Run `uv sync` or ensure using `.venv` interpreter |
| ImportError: common.models | Not running with `PYTHONPATH=src` | Prefix command with `PYTHONPATH=src` or convert project to a proper package name |
| No packets in netcat | Simulator not running / wrong port | Check simulator terminal, verify port 9999 |
| Prometheus not scraping | Wrong target or server not started | Confirm `prometheus.yml` and that app is running on 8000 |

## License

Add license details here (not specified yet).

