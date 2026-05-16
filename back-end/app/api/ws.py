import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings
from app.models.domain import Domain
from app.services.deals import manager

logger = logging.getLogger(__name__)
router = APIRouter()

POLL_INTERVAL = 10  # seconds

_engine = None
_SessionLocal = None


def _session_factory() -> Session | None:
    global _engine, _SessionLocal
    if not settings.DATABASE_URL:
        return None
    if _SessionLocal is None:
        _engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine)
    return _SessionLocal()


def _fetch_deals() -> list[dict]:
    session = _session_factory()
    if session is None:
        return []
    try:
        rows = (
            session.query(Domain)
            .order_by(Domain.score.desc())
            .limit(50)
            .all()
        )
        return [
            {
                "domain": d.name,
                "score": round(d.score or 0, 2),
                "estValue": round(d.est_value or 0, 2),
            }
            for d in rows
        ]
    except Exception as exc:
        logger.warning("DB fetch failed: %s", exc)
        return []
    finally:
        session.close()


@router.websocket("/ws/deals")
async def ws_deals(ws: WebSocket):
    await manager.connect(ws)
    try:
        # send initial snapshot immediately on connect
        deals = await asyncio.to_thread(_fetch_deals)
        await ws.send_json(deals)

        # push a fresh snapshot every POLL_INTERVAL seconds
        while True:
            await asyncio.sleep(POLL_INTERVAL)
            deals = await asyncio.to_thread(_fetch_deals)
            await ws.send_json(deals)
    except WebSocketDisconnect:
        pass
    except Exception as exc:
        logger.warning("WS connection error: %s", exc)
    finally:
        manager.disconnect(ws)
