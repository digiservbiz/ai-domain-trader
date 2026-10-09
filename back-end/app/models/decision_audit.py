from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from app.db.base import Base


class DecisionAudit(Base):
    __tablename__ = "decision_audits"
    __table_args__ = (UniqueConstraint("user_id", "audit_id", name="uq_decision_audits_user_hash"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    audit_id = Column(String(64), nullable=False, index=True)
    domain = Column(String(253), nullable=False, index=True)
    recommendation = Column(String(64), nullable=False, index=True)
    hash_algorithm = Column(String(16), nullable=False, default="sha256")
    payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
