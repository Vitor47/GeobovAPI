from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    serial_number = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=False, index=True)

    cattle_id = Column(
        Integer,
        ForeignKey("cattle.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    transmission_interval_minutes = Column(Integer, default=5, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    cattle = relationship("Cattle", back_populates="device")
    company = relationship("Company", back_populates="devices")
