from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.adapters.models.base import BaseModel


class Device(BaseModel):
    __tablename__ = "devices"

    serial_number = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)

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

    cattle = relationship("Cattle", back_populates="device")
    company = relationship("Company", back_populates="devices")

    def __str__(self) -> str:
        label = self.name or self.serial_number
        return (
            f"{self.serial_number} ({label})" if self.name else str(self.serial_number)
        )
