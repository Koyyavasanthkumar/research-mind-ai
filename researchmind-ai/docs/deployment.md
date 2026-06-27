# Deployment

ResearchMind AI supports local development, Docker, Docker Compose, Render, Railway, and Ubuntu VPS deployment.

## Environment

Create `.env` for development:

```bash
cp .env.example .env
```

Create `.env.production` for production:

```bash
cp .env.production.example .env.production
```

Production requires:

- `APP_ENV=production`
- `GEMINI_API_KEY`
- `TAVILY_API_KEY`
- `JWT_SECRET` with at least 32 characters
- explicit `ALLOWED_ORIGINS`

## Local Backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn backend.main:app --reload --port 8000
```

## Local Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Docker Development

```bash
docker compose up --build
```

## Docker Production

```bash
docker compose -f docker-compose.prod.yml up --build -d
```

The production stack includes:

- backend FastAPI service
- frontend static Nginx service
- reverse proxy Nginx service
- persistent backend volume for SQLite, ChromaDB, logs, and reports

## Nginx

The production Nginx config provides:

- reverse proxy routing
- `/api` routing to backend
- static frontend routing
- gzip compression
- security headers
- asset caching
- backend timeout settings

## Render

Use `render.yaml`.

1. Create a Render Blueprint.
2. Connect the repository.
3. Add required secrets.
4. Confirm `/health` returns `ok`.

## Railway

Use `railway.json`.

1. Create a Railway project.
2. Select Dockerfile deployment.
3. Add required environment variables.
4. Verify `/health`.

## Ubuntu VPS

1. Install Docker and Docker Compose.
2. Clone the repository.
3. Create `.env.production`.
4. Run `docker compose -f docker-compose.prod.yml up --build -d`.
5. Add TLS with Certbot or a managed proxy.
6. Persist `/data` or Docker volumes for SQLite, ChromaDB, logs, and PDFs.

## Health and Metrics

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## Troubleshooting

- **Production startup fails:** validate `JWT_SECRET`, `GEMINI_API_KEY`, `TAVILY_API_KEY`, and `ALLOWED_ORIGINS`.
- **PDF not found:** ensure `REPORTS_DIR` is writable and persistent.
- **Memory search empty:** verify ChromaDB path is writable.
- **401 response:** pass a valid bearer access token.
- **429 response:** reduce request rate or increase rate limit values.
- **Search quality low:** verify Tavily key and query depth.
