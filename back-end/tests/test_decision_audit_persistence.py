import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.decision_audit import DecisionAudit
from app.models.user import User
from app.services.decision_audit import build_decision_audit


def test_decision_audit_record_persists_payload_and_is_user_scoped():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine)
    db = session_factory()
    try:
        owner = User(email="owner@example.com", hashed_password="not-used")
        other = User(email="other@example.com", hashed_password="not-used")
        db.add_all([owner, other])
        db.commit()
        snapshot = build_decision_audit(
            {
                "domain": "Example.COM.",
                "recommendation": "WATCH",
                "inputs": {"estimated_resale_value": 200},
                "financials": {"expected_net_profit": 20},
                "policy": {"max_cost": 100},
                "reasons": ["evidence confidence is limited"],
            },
            evidence_sources=[{"provider": "test-fixture", "locator": "case-1"}],
        )
        record = DecisionAudit(
            user_id=owner.id,
            audit_id=snapshot["audit_id"],
            domain=snapshot["domain"],
            recommendation=str(snapshot["recommendation"]),
            hash_algorithm=snapshot["hash_algorithm"],
            payload_json=json.dumps(snapshot, sort_keys=True, separators=(",", ":"), allow_nan=False),
        )
        db.add(record)
        db.commit()

        assert db.query(DecisionAudit).filter(
            DecisionAudit.audit_id == snapshot["audit_id"],
            DecisionAudit.user_id == owner.id,
        ).one().domain == "example.com"
        assert db.query(DecisionAudit).filter(
            DecisionAudit.audit_id == snapshot["audit_id"],
            DecisionAudit.user_id == other.id,
        ).count() == 0
        stored = json.loads(record.payload_json)
        assert stored["paper_trading_only"] is True
        assert stored["purchase_executed"] is False
        assert stored["audit_id"] == snapshot["audit_id"]
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
