# AI Domain Trader — Setup Script for Windows (PowerShell)
# Run with: .\setup.ps1
# If blocked by execution policy: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

$ErrorActionPreference = "Stop"

function Info  { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Warn  { param($msg) Write-Host "[!]  $msg" -ForegroundColor Yellow }
function Fail  { param($msg) Write-Host "[X]  $msg" -ForegroundColor Red; exit 1 }

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "    AI Domain Trader - Setup (Windows)    " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. check prerequisites ─────────────────────────────────────────────────
Info "Checking prerequisites..."

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Fail "Git is not installed. Download from: https://git-scm.com/downloads"
}
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Fail "Docker is not installed. Download from: https://www.docker.com/products/docker-desktop/"
}

try { docker info | Out-Null } catch {
    Fail "Docker is not running. Please start Docker Desktop and try again."
}
try { docker compose version | Out-Null } catch {
    Fail "Docker Compose not found. Update Docker Desktop to the latest version."
}

Info "Git, Docker, and Docker Compose are ready."

# ── 2. create .env file ────────────────────────────────────────────────────
if (Test-Path ".env") {
    Warn ".env already exists — skipping creation."
} else {
    Copy-Item ".env.example" ".env"
    Info "Created .env from .env.example"
}

# ── 3. prompt for OpenRouter API key ──────────────────────────────────────
$envContent = Get-Content ".env" -Raw
if ($envContent -match "sk-or-xxx") {
    Write-Host ""
    Write-Host "  An OpenRouter API key is required for domain name generation."
    Write-Host "  Get a free key at: https://openrouter.ai/keys"
    Write-Host ""
    $OrKey = Read-Host "  Paste your OpenRouter API key (sk-or-...)"
    if ($OrKey -like "sk-or-*") {
        $envContent = $envContent -replace "OPENROUTER_API_KEY=sk-or-xxx", "OPENROUTER_API_KEY=$OrKey"
        Set-Content ".env" $envContent
        Info "API key saved to .env"
    } else {
        Warn "Key doesn't look right (expected sk-or-...). Edit .env manually to set it."
    }
} else {
    Info "OpenRouter API key already set."
}

# ── 4. optional: choose free model ────────────────────────────────────────
Write-Host ""
Write-Host "  Which model would you like to use for domain generation?"
Write-Host "  1) openai/gpt-4o-mini                   (default - best quality)"
Write-Host "  2) mistralai/mistral-7b-instruct:free   (free, good quality)"
Write-Host "  3) meta-llama/llama-3-8b-instruct:free  (free, fast)"
Write-Host "  4) Keep current setting"
Write-Host ""
$ModelChoice = Read-Host "  Enter choice [1-4, default=1]"
$envContent = Get-Content ".env" -Raw
switch ($ModelChoice) {
    "2" {
        $envContent = $envContent -replace "OPENROUTER_MODEL=.*", "OPENROUTER_MODEL=mistralai/mistral-7b-instruct:free"
        Set-Content ".env" $envContent
        Info "Model set to mistralai/mistral-7b-instruct:free"
    }
    "3" {
        $envContent = $envContent -replace "OPENROUTER_MODEL=.*", "OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free"
        Set-Content ".env" $envContent
        Info "Model set to meta-llama/llama-3-8b-instruct:free"
    }
    "4" { Info "Keeping current model setting." }
    default { Info "Using default: openai/gpt-4o-mini" }
}

# ── 5. build and start ─────────────────────────────────────────────────────
Write-Host ""
Info "Building and starting all services (this takes 3-5 min on first run)..."
Write-Host ""
docker compose up --build -d

# ── 6. wait for backend ────────────────────────────────────────────────────
Write-Host ""
Info "Waiting for the backend to be ready..."
$maxWait = 90
$waited  = 0
$ready   = $false
while ($waited -lt $maxWait) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:8000/healthz" -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch {}
    Start-Sleep -Seconds 3
    $waited += 3
    Write-Host -NoNewline "."
}
Write-Host ""
if ($ready) { Info "Backend is up." }
else { Warn "Backend didn't respond after ${maxWait}s. Check logs: docker compose logs backend" }

# ── 7. trigger initial scrape ──────────────────────────────────────────────
Write-Host ""
Info "Triggering initial domain scrape (populates the deals page)..."
try {
    docker compose exec -T celery-worker `
        celery -A app.celery_app.celery call app.tasks.scrapers.scrape_expired_domains 2>&1 | Out-Null
    Info "Scraper triggered."
} catch {
    Warn "Could not trigger scraper automatically. Run it manually later."
}

# ── 8. done ────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  All done! Open these URLs in your browser:"              -ForegroundColor Cyan
Write-Host ""
Write-Host "  App        ->  http://localhost:3000"                    -ForegroundColor White
Write-Host "  Live Deals ->  http://localhost:3000/deals"              -ForegroundColor White
Write-Host "  API Docs   ->  http://localhost:8000/docs"               -ForegroundColor White
Write-Host ""
Write-Host "  Useful commands:"
Write-Host "  docker compose logs -f     - view all logs"
Write-Host "  docker compose down        - stop everything"
Write-Host "  docker compose down -v     - stop and delete all data"
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""
