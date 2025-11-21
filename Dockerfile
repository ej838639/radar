# Build a slim Python image that uses uv to install dependencies declared in pyproject.toml
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    # make src/ available as a module for `python -m app`
    PYTHONPATH=/app/src \
    # uv installs to ~/.local/bin by default
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Install curl to fetch uv installer
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager / resolver)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# Copy dependency metadata first (enable Docker layer caching)
COPY pyproject.toml ./
COPY README.md ./
# Optional: copy lock if you have it
# COPY uv.lock ./

# Create a local venv and sync dependencies
# (No dev deps; add --all-extras/--group dev if needed)
RUN uv venv .venv && uv sync

# Put venv python on PATH
ENV PATH="/app/.venv/bin:${PATH}"

# Copy application source
COPY src ./src
# (Optional) copy README and docs for reference inside image
# COPY README.md ./README.md

# The app exposes Prometheus on 8000 and listens UDP on 9999
EXPOSE 8000/tcp
EXPOSE 9999/udp

# Default command launches the app
CMD ["python", "-m", "app"]