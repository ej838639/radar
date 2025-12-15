# Radar Project

Simulated radar data pipeline with:
- Simulator that emits JSON tracks at a configurable rate
- UDP track/health/frame ingestion
- Prometheus metrics exposed at `http://localhost:8000/metrics`

## Start the radar simulation and data ingestion

Install Docker Desktop for Mac if not already installed.

Build and start both the application and simulator containers in detached mode:

```bash
docker-compose up --build -d
```

## View the logs

View the logs from the application to see received UDP messages:

```bash
docker-compose logs -f app
```

Ctrl-C to exit showing the stream of logs.

## Radar app in Prometheus format

For Prometheus metrics, navigate to `http://localhost:8000/metrics` and look for the following metrics:

Ingest:
- `radar_ingest_packets_total`
- `radar_packets_total{kind="track"}`
- `radar_packets_total{kind="health"}`

Health:
- `radar_mode`
- `radar_temperature_c`
- `radar_cpu_pct`
- `supply_v`

## Prometheus Server UI
Query, visualize, and alert on metrics.

Install Prometheus:

- macOS (Homebrew):
  ```bash
  brew install prometheus
  ```
- Windows (PowerShell + Chocolatey):
  ```powershell
  choco install prometheus
  ```
  If you do not use Chocolatey, download the Windows tarball from https://prometheus.io/download/ and extract it, then run `prometheus.exe` with the args shown below.

Start the Prometheus server to scrapes metrics from Port 8000 at regular intervals and store historical time-series data.

```bash
prometheus --config.file=./prometheus.yml --storage.tsdb.path=./.prometheus-data
```

View the Prometheus UI at http://localhost:9090/
- Query the same metrics listed above.
- Exit the UI with Ctrl-C in the terminal.

When done reviewing the project, stop the containers:

```bash
docker-compose down
```

To remove the images:

```bash
# Remove the specific images
docker rmi radar-sim:latest radar-app:latest
```

This cleanup ensures a fresh start when you run `docker-compose up` again later.

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
