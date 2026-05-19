from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.base import get_db
from app.core.security import get_current_user
from app.models.snipe_target import SnipeTarget

router = APIRouter(prefix="/snipe", tags=["snipe"])


class SnipeCreate(BaseModel):
    domain: str
    max_bid: float


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


@router.get("")
def list_snipe_targets(
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    targets = db.query(SnipeTarget).all()
    return [_target_dict(t) for t in targets]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_snipe_target(
    body: SnipeCreate,
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    existing = db.query(SnipeTarget).filter_by(domain=body.domain).first()
    if existing:
        raise HTTPException(status_code=400, detail="Domain already has a snipe target")
    target = SnipeTarget(domain=body.domain, max_bid=body.max_bid)
    db.add(target)
    db.commit()
    db.refresh(target)

    from app.tasks.auction import snipe
    snipe.delay(body.domain, body.max_bid)

    return _target_dict(target)


@router.delete("/{domain}")
def delete_snipe_target(
    domain: str,
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    target = db.query(SnipeTarget).filter_by(domain=domain).first()
    if not target:
        raise HTTPException(status_code=404, detail="Snipe target not found")
    db.delete(target)
    db.commit()
    return {"deleted": True, "domain": domain}


@router.post("/{domain}/trigger")
def trigger_snipe(
    domain: str,
    db: Session = Depends(get_db),
    _user: dict = Depends(get_current_user),
):
    target = db.query(SnipeTarget).filter_by(domain=domain).first()
    if not target:
        raise HTTPException(status_code=404, detail="Snipe target not found")

    from app.tasks.auction import snipe
    snipe.delay(target.domain, target.max_bid)

    return {"triggered": True, "domain": domain}
