"""Authenticated, tenant-scoped decision audit history endpoints."""
import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.base import get_db
from app.models.decision_audit import DecisionAudit
from app.models.user import User
from app.services.decision_audit import build_decision_audit

router = APIRouter(prefix="/decision-audits", tags=["decision-audits"])


class DecisionAuditCreate(BaseModel):
    decision: dict[str, Any]
    evidence_sources: list[dict[str, Any]] = Field(default_factory=list)


def _user_id(db: Session, current_user: dict) -> int:
    user = db.query(User).filter(User.email == current_user["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user.id


def _record_dict(record: DecisionAudit) -> dict[str, Any]:
    payload = json.loads(record.payload_json)
    return {
        "audit_id": record.audit_id,
        "domain": record.domain,
        "recommendation": record.recommendation,
        "hash_algorithm": record.hash_algorithm,
        "created_at": record.created_at.isoformat(),
        "payload": payload,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_decision_audit(
    body: DecisionAuditCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = _user_id(db, current_user)
    try:
        snapshot = build_decision_audit(body.decision, evidence_sources=body.evidence_sources)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    existing = db.query(DecisionAudit).filter(DecisionAudit.audit_id == snapshot["audit_id"]).first()
    if existing:
        if existing.user_id != user_id:
            # Do not reveal another account's record or whether its content matched.
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Audit snapshot already exists")
        return {**_record_dict(existing), "created": False}

    record = DecisionAudit(
        user_id=user_id,
        audit_id=snapshot["audit_id"],
        domain=snapshot["domain"],
        recommendation=str(snapshot["recommendation"]),
        hash_algorithm=snapshot["hash_algorithm"],
        payload_json=json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False),
    )
    db.add(record)
    try:
        db.commit()
    except Exception:
        db.rollback()
        # A concurrent identical insert can hit the unique constraint; return the
        # existing same-user record only after re-reading it safely.
        existing = db.query(DecisionAudit).filter(DecisionAudit.audit_id == snapshot["audit_id"]).first()
        if existing and existing.user_id == user_id:
            return {**_record_dict(existing), "created": False}
        raise
    db.refresh(record)
    return {**_record_dict(record), "created": True}


@router.get("")
def list_decision_audits(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    domain: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = _user_id(db, current_user)
    query = db.query(DecisionAudit).filter(DecisionAudit.user_id == user_id)
    if domain:
        query = query.filter(DecisionAudit.domain == domain.strip().lower().rstrip("."))
    total = query.count()
    records = query.order_by(DecisionAudit.created_at.desc(), DecisionAudit.id.desc()).offset(offset).limit(limit).all()
    return {"items": [_record_dict(record) for record in records], "total": total, "limit": limit, "offset": offset}


@router.get("/{audit_id}")
def get_decision_audit(
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    user_id = _user_id(db, current_user)
    record = db.query(DecisionAudit).filter(
        DecisionAudit.audit_id == audit_id,
        DecisionAudit.user_id == user_id,
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Decision audit not found")
    return _record_dict(record)
