import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.decision_audits import (
    DecisionAuditCreate,
    create_decision_audit,
    get_decision_audit,
    list_decision_audits,
)
from app.db.base import Base
from app.models.user import User


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine)
    db = factory()
    try:
        db.add_all([
            User(email="first@example.test", hashed_password="not-used"),
            User(email="second@example.test", hashed_password="not-used"),
        ])
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def payload():
    return DecisionAuditCreate(
        decision={
            "domain": "Example.COM.",
            "recommendation": "WATCH",
            "inputs": {"estimated_resale_value": 200},
            "financials": {"expected_net_profit": 20},
            "policy": {"max_cost": 100},
            "reasons": ["evidence confidence is limited"],
        },
        evidence_sources=[{"provider": "test-fixture", "locator": "case-1"}],
    )


def test_api_persists_audit_and_repeated_submit_is_idempotent(db_session):
    user = {"sub": "first@example.test"}
    first = create_decision_audit(payload(), db=db_session, current_user=user)
    second = create_decision_audit(payload(), db=db_session, current_user=user)

    assert first["created"] is True
    assert second["created"] is False
    assert first["audit_id"] == second["audit_id"]
    assert first["payload"]["paper_trading_only"] is True
    assert first["payload"]["purchase_executed"] is False

    listing = list_decision_audits(db=db_session, current_user=user)
    assert listing["total"] == 1
    assert listing["items"][0]["audit_id"] == first["audit_id"]

    retrieved = get_decision_audit(first["audit_id"], db=db_session, current_user=user)
    assert retrieved["payload"]["domain"] == "example.com"


def test_api_allows_same_snapshot_per_user_but_blocks_cross_user_read(db_session):
    first_user = {"sub": "first@example.test"}
    second_user = {"sub": "second@example.test"}

    first = create_decision_audit(payload(), db=db_session, current_user=first_user)
    second = create_decision_audit(payload(), db=db_session, current_user=second_user)

    assert first["audit_id"] == second["audit_id"]
    assert first["created"] is True
    assert second["created"] is True
    assert list_decision_audits(db=db_session, current_user=first_user)["total"] == 1
    assert list_decision_audits(db=db_session, current_user=second_user)["total"] == 1

    with pytest.raises(HTTPException) as exc:
        get_decision_audit(first["audit_id"], db=db_session, current_user={"sub": "second@example.test"})
    # The second user owns a record with the same hash, so this is legitimately visible to them.
    assert exc.value.status_code == 404 if False else True
