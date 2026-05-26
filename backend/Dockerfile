FROM python:3.12-slim

# Create a non-root user to run the app
RUN addgroup --system meridian && adduser --system --ingroup meridian meridian

WORKDIR /app

# Copy only the files needed for installation
COPY pyproject.toml ./
COPY meridian/ ./meridian/

# Install base dependencies only (no [swarm] extra — swarm runs via cloud HTTP API)
RUN pip install --no-cache-dir .

# DATA_DIR default; can be overridden via env var (mount a persistent disk at /data)
ENV DATA_DIR=/data

# Create the data directory and make it writable by the app user
RUN mkdir -p /data && chown -R meridian:meridian /data /app

USER meridian

EXPOSE 8000

# Shell-form CMD so $PORT (injected by Render/Railway) is expanded at runtime
CMD uvicorn meridian.api.server:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}
