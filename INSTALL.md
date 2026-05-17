# AI Domain Trader — Installation Guide

## Prerequisites

Install these tools before starting. Click each link for official instructions.

| Tool | Minimum version | Check |
|---|---|---|
| [Git](https://git-scm.com/downloads) | any | `git --version` |
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | 24+ | `docker --version` |
| Docker Compose | included in Docker Desktop | `docker compose version` |

> **Windows users:** use [Docker Desktop with WSL 2](https://docs.docker.com/desktop/wsl/).  
> **Mac users:** Docker Desktop for Mac includes Compose — no extras needed.

---

## Step 1 — Clone the repository

```bash
git clone https://github.com/digiservbiz/ai-domain-trader.git
cd ai-domain-trader
git checkout claude/analyze-repo-gdyml
```

---

## Step 2 — Get your OpenRouter API key (free)

1. Go to **https://openrouter.ai/keys**
2. Sign up for a free account
3. Click **Create Key** — copy the key (starts with `sk-or-`)

> OpenRouter gives you access to many models. The default used here (`openai/gpt-4o-mini`)
> costs ~$0.15 per million tokens. Free alternatives are listed in Step 3.

---

## Step 3 — Create your `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Open `.env` in any text editor and fill in your values:

```env
# REQUIRED — your OpenRouter key from Step 2
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxxxxxx

# Model to use for domain name generation
# Paid (cheap):  openai/gpt-4o-mini
# Free:          mistralai/mistral-7b-instruct:free
#                meta-llama/llama-3-8b-instruct:free
OPENROUTER_MODEL=openai/gpt-4o-mini

# Leave these as-is — Docker handles them automatically
DATABASE_URL=postgresql://trader:trader@db:5432/domains
REDIS_URL=redis://redis:6379/0

# Optional — only needed for real Moz SEO data
# Leave as xxx to skip (the app works without it)
MOZ_ACCESS_ID=xxx
MOZ_SECRET_KEY=xxx

# Optional — GoDaddy and Reddit API keys (not needed for MVP)
GODADDY_KEY=xxx
GODADDY_SECRET=xxx
REDDIT_CLIENT=xxx
REDDIT_SECRET=xxx
```

> **Minimum to run:** only `OPENROUTER_API_KEY` needs a real value.  
> Everything else can stay as `xxx` for local testing.

---

## Step 4 — Start the project

```bash
docker compose up --build
```

This will:
1. Build the backend and frontend Docker images (~3–5 min on first run)
2. Start PostgreSQL and Redis
3. Run database migrations automatically
4. Start the API server, Celery worker, Celery scheduler, and frontend

You'll know it's ready when you see lines like:
```
backend-1       | INFO:     Application startup complete.
frontend-1      | ▲ Next.js 14.2.3
frontend-1      | ✓ Ready on http://localhost:3000
celery-worker-1 | celery@... ready.
```

---

## Step 5 — Open the app

| URL | What you'll see |
|---|---|
| http://localhost:3000 | Home page |
| http://localhost:3000/deals | Live domain deals feed |
| http://localhost:8000/docs | Interactive API docs (Swagger UI) |

---

## Step 6 — Test the API manually

Open a new terminal and run:

```bash
# 1. Health check
curl http://localhost:8000/healthz

# 2. Generate domain name ideas
curl "http://localhost:8000/generate?niche=fintech&keywords=pay,fast,wallet"

# 3. Value a specific domain
curl http://localhost:8000/value/payfast.io
```

Expected responses:

```json
// /healthz
{"status": "ok"}

// /generate
{"domains": ["payvault.io", "fastpay.ai", "walletfast.com", ...]}

// /value/payfast.io
{"domain": "payfast.io", "estValue": 142.50}
```

---

## Step 7 — Trigger the domain scraper immediately

The scraper runs automatically every 6 hours. To populate the deals page right away:

```bash
docker compose exec celery-worker \
  celery -A app.celery_app.celery call app.tasks.scrapers.scrape_expired_domains
```

Wait 20–30 seconds, then refresh **http://localhost:3000/deals**.  
You should see live expired domains with scores and estimated values.

---

## Stopping the project

```bash
# Stop all containers (keeps data)
docker compose down

# Stop and delete all data (fresh start)
docker compose down -v
```

---

## Troubleshooting

### Port already in use
If ports 3000, 8000, 5432, or 6379 are taken by another app:

```bash
# Find what's using port 8000
lsof -i :8000      # Mac/Linux
netstat -ano | findstr :8000   # Windows
```

Either stop the other app or change the port in `docker-compose.yml`  
(e.g. `"8001:8000"` maps local port 8001 to container port 8000).

### Backend fails to start
Check the logs:
```bash
docker compose logs backend
```

Most common cause: `DATABASE_URL` not reachable. Make sure the `db` container is healthy:
```bash
docker compose ps
```

### Deals page shows "No deals available yet"
The scraper hasn't run yet. Trigger it manually with the command in Step 7.

### Domain generation returns an empty list
Your `OPENROUTER_API_KEY` is missing or invalid. Double-check your `.env` file and restart:
```bash
docker compose down && docker compose up
```

### Want to see all logs at once
```bash
docker compose logs -f
```

### Want to see logs for one service only
```bash
docker compose logs -f backend
docker compose logs -f celery-worker
docker compose logs -f celery-beat
```

---

## Service overview

| Service | Port | Purpose |
|---|---|---|
| `frontend` | 3000 | Next.js UI |
| `backend` | 8000 | FastAPI REST + WebSocket |
| `db` | 5432 | PostgreSQL (domain data) |
| `redis` | 6379 | Celery message broker |
| `celery-worker` | — | Runs scraper tasks |
| `celery-beat` | — | Schedules scrapers every 3–6h |
| `migrate` | — | Runs DB migrations on startup, then exits |
