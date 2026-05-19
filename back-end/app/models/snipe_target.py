from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.base import Base


class SnipeTarget(Base):
    __tablename__ = "snipe_targets"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True, nullable=False)
    max_bid = Column(Float, nullable=False)
    status = Column(String, default="watching")
    current_bid = Column(Float, nullable=True)
    last_checked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
