import os
import sentry_sdk

_sentry_dsn = os.getenv("SENTRY_DSN")
if _sentry_dsn:
    sentry_sdk.init(dsn=_sentry_dsn, traces_sample_rate=0.2, environment=os.getenv("ENVIRONMENT", "production"))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from slowapi import _rate_limit_exceeded_handler  # noqa: E402
from slowapi.errors import RateLimitExceeded  # noqa: E402
from app.api.routes import router  # noqa: E402
from app.api.ws import router as ws_router  # noqa: E402
from app.api.auth import router as auth_router  # noqa: E402
from app.api.portfolio import router as portfolio_router  # noqa: E402
from app.api.snipe import router as snipe_router  # noqa: E402
from app.api.decision_audits import router as decision_audits_router  # noqa: E402
from app.core.rate_limit import limiter  # noqa: E402

app = FastAPI(title="AI Domain Trader")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

_frontend = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[_frontend],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(ws_router)
app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(snipe_router)
app.include_router(decision_audits_router)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
