import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router
from app.api.ws import router as ws_router
from app.api.auth import router as auth_router
from app.api.portfolio import router as portfolio_router
from app.api.snipe import router as snipe_router

limiter = Limiter(key_func=get_remote_address)

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


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
