# Radar Project

Simulated radar data pipeline with:
- Simulator that emits JSON tracks at a configurable rate
- UDP track/health/frame ingestion
- Prometheus metrics exposed at `http://localhost:8000/metrics`

## Quick Start (Docker Compose)

Install Docker Desktop for Mac if not already installed.

Build and start both the application and simulator containers in detached mode:

```bash
docker-compose up --build -d
```

View the logs from the application to see received UDP messages:

```bash
docker-compose logs -f app
```

You can also view logs from both services:

```bash
docker-compose logs -f'
```
Ctrl-C to exit.

Stop the containers:

```bash
docker-compose down
```

To clean up and remove containers, networks, and images:

```bash
# Remove all stopped containers
docker container prune -f

# Remove the specific images
docker rmi radar-sim:latest radar-app:latest
```

This cleanup ensures a fresh start when you run `docker-compose up` again later.

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
  app.py                    # Main app: exposes metrics & ingests UDP
  adapter/
    ingest.py               # UDP datagram ingestion
    parser.py               # Parse JSON messages (Track, Health, Frame)
  common/
    models.py               # Pydantic models (Track, HealthStatus, Frame)
  tools/
    sim_udp.py              # UDP simulator with configurable host/port
docs/
  requirements.md           # Project requirements
  system_architecture.md    # Architecture documentation
  interface_specifications.md # Interface specs
tests/                      # Test suite (empty)
docker-compose.yml          # Multi-container orchestration (app + simulator)
Dockerfile                  # Main app container image
Dockerfile.simulator        # Simulator container image
prometheus.yml              # Prometheus scrape config
pyproject.toml              # Project metadata & dependencies
uv.lock                     # Dependency lock file
```
