# Soundverse Play API

A lightweight FastAPI backend service for browsing and streaming short audio previews. Users can list available sound clips, stream audio in real time, view playback statistics, and add new clips -- all secured behind API key authentication and monitored with Prometheus and Grafana.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.x (sync) |
| HTTP Client | httpx (streaming proxy) |
| Monitoring | Prometheus + Grafana |
| Containerization | Docker & Docker Compose |
| Deployment | Render |
| CI/CD | GitHub Actions |
| Linting | Ruff |
| Testing | pytest + FastAPI TestClient |

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for full-stack setup)

### Full Stack with Docker

```bash
git clone https://github.com/your-org/soundverse.git
cd soundverse
docker-compose up --build
```

This starts four services:

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| PostgreSQL | localhost:5432 |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |

### Local Development (without Docker)

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your database URL and API key

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/play` | X-API-Key | List all sound clips |
| `POST` | `/play` | X-API-Key | Create a new sound clip |
| `GET` | `/play/{clip_id}/stream` | X-API-Key | Stream clip audio (proxied MP3) |
| `GET` | `/play/{clip_id}/stats` | X-API-Key | Get clip metadata and play count |
| `GET` | `/health` | None | Health check (database connectivity) |
| `GET` | `/metrics` | None | Prometheus metrics |

## Authentication

All `/play` endpoints require an `X-API-Key` header. The key is configured via the `API_KEY` environment variable.

The `/health` and `/metrics` endpoints are unauthenticated so that Render health checks and Prometheus scraping work without credentials.

## Example API Calls

### List all clips

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/play
```

### Stream a clip

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/play/1/stream --output clip.mp3
```

### Get clip stats

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/play/1/stats
```

### Create a new clip

```bash
curl -X POST http://localhost:8000/play \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Track",
    "description": "A fresh beat",
    "genre": "electronic",
    "duration": 120.0,
    "audio_url": "https://example.com/track.mp3"
  }'
```

### Health check

```bash
curl http://localhost:8000/health
```

## Monitoring

### Prometheus

Available at http://localhost:9090 when running with Docker Compose. Scrapes the `/metrics` endpoint every 15 seconds.

Built-in metrics include:

- `soundverse_requests_total` -- total HTTP requests by method, path, and status
- `soundverse_request_duration_seconds` -- request latency histogram
- `soundverse_streams_total` -- total audio streams by clip ID
- `soundverse_stream_duration_seconds` -- stream latency histogram by clip ID

### Grafana

Available at http://localhost:3000 with default credentials `admin` / `admin`.

A pre-provisioned dashboard named "Soundverse Play API" is loaded automatically and includes four panels:

1. **Total API Requests Over Time** -- request rate across all endpoints
2. **Streams Per Clip ID** -- per-clip stream rate
3. **Response Latency (p50/p95/p99)** -- latency percentiles
4. **Current Play Counts by Clip** -- cumulative stream counts

A `$clip_id` template variable allows filtering by individual clips.

## Project Structure

```
soundverse/
├── app/
│   ├── __init__.py
│   ├── config.py              # Pydantic settings (env vars)
│   ├── database.py            # SQLAlchemy engine, session, get_db
│   ├── exceptions.py          # Custom exceptions and handlers
│   ├── main.py                # FastAPI app factory, lifespan, middleware
│   ├── metrics.py             # Custom Prometheus counters
│   ├── models.py              # SoundClip ORM model
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── seed.py                # Database seeder (6 sample clips)
│   ├── routers/
│   │   ├── __init__.py
│   │   └── play.py            # /play route handlers
│   └── services/
│       ├── __init__.py
│       └── clip_service.py    # Business logic layer
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Test fixtures (TestClient, test DB)
│   ├── test_play.py           # Endpoint tests
│   └── test_metrics.py        # Metrics and health tests
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           │   └── datasource.yml
│           └── dashboards/
│               ├── dashboard.yml
│               └── soundverse.json
├── .github/
│   └── workflows/
│       ├── ci.yml             # Lint + test pipeline
│       └── deploy.yml         # Render deploy hook
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://soundverse:soundverse@localhost:5432/soundverse` |
| `API_KEY` | Secret key for X-API-Key authentication | `default-dev-key` |
| `APP_NAME` | Application name | `Soundverse Play API` |
| `APP_VERSION` | Application version | `1.0.0` |
| `DEBUG` | Enable debug mode | `false` |
| `STREAM_CHUNK_SIZE` | Bytes per streaming chunk | `8192` |

## Testing

Tests use an in-memory SQLite database and do not require PostgreSQL.

```bash
# Install test dependencies
pip install pytest

# Run all tests
pytest tests/ -v

# Run a specific test file
pytest tests/test_play.py -v

# Run with short tracebacks
pytest tests/ -v --tb=short
```

## Deployment

### Render

The project includes a `render.yaml` blueprint for one-click deployment to Render.

1. Push the repository to GitHub.
2. In the Render dashboard, create a new **Blueprint** and connect the repository.
3. Render will provision the web service and a free PostgreSQL database from `render.yaml`.
4. Set the `API_KEY` environment variable manually in the Render dashboard (it is marked as a secret).
5. The application seeds the database with sample clips on first startup.

**Notes:**
- The free tier has cold starts (~30 seconds after 15 minutes of inactivity).
- The free PostgreSQL database expires after 90 days.

### Deploy Hook

For automated deployments, add a Render Deploy Hook URL as a GitHub Actions secret named `RENDER_DEPLOY_HOOK_URL`. Pushes to `main` will trigger a deployment automatically via the `deploy.yml` workflow.

## CI/CD

Two GitHub Actions workflows are configured:

### CI (`ci.yml`)

Runs on every push and pull request to `main`:

- **Lint job**: Runs `ruff check` and `ruff format --check` against `app/` and `tests/`.
- **Test job**: Spins up a PostgreSQL 16 service container and runs `pytest tests/ -v --tb=short`.

### Deploy (`deploy.yml`)

Runs on pushes to `main` and manual dispatch:

- Triggers the Render Deploy Hook URL stored in GitHub Secrets to deploy the latest code.
