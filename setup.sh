#!/usr/bin/env bash
set -euo pipefail

# ── colours ────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[✔]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✘]${NC} $*"; exit 1; }

echo ""
echo "╔══════════════════════════════════════╗"
echo "║      AI Domain Trader — Setup        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── 1. check prerequisites ─────────────────────────────────────────────────
info "Checking prerequisites..."

command -v git    >/dev/null 2>&1 || error "Git is not installed. https://git-scm.com/downloads"
command -v docker >/dev/null 2>&1 || error "Docker is not installed. https://www.docker.com/products/docker-desktop/"

docker info >/dev/null 2>&1 || error "Docker is not running. Please start Docker Desktop and try again."

docker compose version >/dev/null 2>&1 || error "Docker Compose not found. Update Docker Desktop to the latest version."

info "Git, Docker, and Docker Compose are ready."

# ── 2. create .env file ────────────────────────────────────────────────────
if [ -f ".env" ]; then
  warn ".env already exists — skipping creation."
else
  cp .env.example .env
  info "Created .env from .env.example"
fi

# ── 3. prompt for OpenRouter API key ──────────────────────────────────────
if grep -q "sk-or-xxx" .env 2>/dev/null; then
  echo ""
  echo "  An OpenRouter API key is required for domain name generation."
  echo "  Get a free key at: https://openrouter.ai/keys"
  echo ""
  read -rp "  Paste your OpenRouter API key (sk-or-...): " OR_KEY
  if [[ "$OR_KEY" == sk-or-* ]]; then
    sed -i.bak "s|OPENROUTER_API_KEY=sk-or-xxx|OPENROUTER_API_KEY=${OR_KEY}|" .env && rm -f .env.bak
    info "API key saved to .env"
  else
    warn "Key doesn't look right (expected sk-or-...). You can edit .env manually later."
  fi
else
  info "OpenRouter API key already set."
fi

# ── 4. optional: choose free model ────────────────────────────────────────
echo ""
echo "  Which model would you like to use for domain generation?"
echo "  1) openai/gpt-4o-mini         (default — best quality, ~\$0.15/1M tokens)"
echo "  2) mistralai/mistral-7b-instruct:free  (free, good quality)"
echo "  3) meta-llama/llama-3-8b-instruct:free (free, fast)"
echo "  4) Keep current setting"
echo ""
read -rp "  Enter choice [1-4, default=1]: " MODEL_CHOICE
case "${MODEL_CHOICE:-1}" in
  2) sed -i.bak "s|OPENROUTER_MODEL=.*|OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free|" .env && rm -f .env.bak
     info "Model set to mistralai/mistral-7b-instruct:free" ;;
  3) sed -i.bak "s|OPENROUTER_MODEL=.*|OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free|" .env && rm -f .env.bak
     info "Model set to meta-llama/llama-3-8b-instruct:free" ;;
  4) info "Keeping current model setting." ;;
  *) info "Using default: openai/gpt-4o-mini" ;;
esac

# ── 5. build and start ─────────────────────────────────────────────────────
echo ""
info "Building and starting all services (this takes 3–5 min on first run)..."
echo ""
docker compose up --build -d

# ── 6. wait for backend to be ready ───────────────────────────────────────
echo ""
info "Waiting for the backend to be ready..."
MAX_WAIT=90
WAITED=0
until curl -sf http://localhost:8000/healthz >/dev/null 2>&1; do
  if [ "$WAITED" -ge "$MAX_WAIT" ]; then
    warn "Backend didn't respond after ${MAX_WAIT}s. Check logs: docker compose logs backend"
    break
  fi
  sleep 3
  WAITED=$((WAITED + 3))
  echo -n "."
done
echo ""
info "Backend is up."

# ── 7. trigger initial scrape ──────────────────────────────────────────────
echo ""
info "Triggering initial domain scrape (populates the deals page)..."
docker compose exec -T celery-worker \
  celery -A app.celery_app.celery call app.tasks.scrapers.scrape_expired_domains \
  >/dev/null 2>&1 && info "Scraper triggered." || warn "Could not trigger scraper — run it manually later."

# ── 8. done ────────────────────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║  All done! Open these URLs in your browser:          ║"
echo "║                                                      ║"
echo "║  🌐  App          http://localhost:3000              ║"
echo "║  📋  Live Deals   http://localhost:3000/deals        ║"
echo "║  📖  API Docs     http://localhost:8000/docs         ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Useful commands:"
echo "  docker compose logs -f          — view all logs"
echo "  docker compose down             — stop everything"
echo "  docker compose down -v          — stop and delete all data"
echo ""
