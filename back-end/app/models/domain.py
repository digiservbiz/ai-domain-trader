from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base
class Domain(Base):
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    score = Column(Float)
    est_value = Column(Float)
