from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import get_current_user
from app.db.base import get_db
from app.models.snipe_target import SnipeTarget
from app.models.user import User

router = APIRouter(prefix="/snipe", tags=["snipe"])


class SnipeCreate(BaseModel):
    domain: str
    max_bid: float = Field(gt=0, le=100)


def _target_dict(t: SnipeTarget) -> dict:
    return {
        "id": t.id,
        "domain": t.domain,
        "max_bid": t.max_bid,
        "status": t.status,
        "current_bid": t.current_bid,
        "last_checked": t.last_checked.isoformat() if t.last_checked else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }


def _user_id(db: Session, current_user: dict) -> int:
    user = db.query(User).filter(User.email == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user.id


@router.get("")
def list_snipe_targets(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = _user_id(db, current_user)
    targets = db.query(SnipeTarget).filter(SnipeTarget.user_id == user_id).all()
    return [_target_dict(t) for t in targets]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_snipe_target(body: SnipeCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = _user_id(db, current_user)
    existing = db.query(SnipeTarget).filter(SnipeTarget.user_id == user_id, SnipeTarget.domain == body.domain).first()
    if existing:
        raise HTTPException(status_code=400, detail="Domain already has a snipe target")
    target = SnipeTarget(user_id=user_id, domain=body.domain, max_bid=body.max_bid, status="paper_watch")
    db.add(target)
    db.commit()
    db.refresh(target)
    return {**_target_dict(target), "mode": settings.TRADING_MODE, "live_bid_queued": False}


@router.delete("/{domain}")
def delete_snipe_target(domain: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = _user_id(db, current_user)
    target = db.query(SnipeTarget).filter(SnipeTarget.user_id == user_id, SnipeTarget.domain == domain).first()
    if not target:
        raise HTTPException(status_code=404, detail="Snipe target not found")
    db.delete(target)
    db.commit()
    return {"deleted": True, "domain": domain}


@router.post("/{domain}/trigger")
def trigger_snipe(domain: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = _user_id(db, current_user)
    target = db.query(SnipeTarget).filter(SnipeTarget.user_id == user_id, SnipeTarget.domain == domain).first()
    if not target:
        raise HTTPException(status_code=404, detail="Snipe target not found")
    if not settings.can_place_live_bids:
        return {"triggered": False, "mode": "paper", "domain": domain, "message": "Live bidding is disabled; no marketplace action was queued."}
    from app.tasks.auction import snipe
    snipe.delay(target.domain, target.max_bid)
    return {"triggered": True, "mode": "live", "domain": domain}
