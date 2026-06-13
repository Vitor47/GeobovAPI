from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    users = relationship("User", back_populates="company")
    cattle = relationship("Cattle", back_populates="company")
    cattle_data = relationship("CattleData", back_populates="company")
    devices = relationship("Device", back_populates="company")
