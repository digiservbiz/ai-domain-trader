from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.base import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    bought_price = Column(Float, nullable=False)
    bought_at = Column(DateTime, default=datetime.utcnow, nullable=False)
