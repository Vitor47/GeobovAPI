from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.adapters.models.base import BaseModel


class Gateway(BaseModel):
    """
    Farm LoRa receiver that authenticates to the API and forwards
    collar telemetry (device serial + GPS) for its company.
    """

    __tablename__ = "gateways"

    serial_number = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    api_key = Column(String, unique=True, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)

    company = relationship("Company", back_populates="gateways")

    def __str__(self) -> str:
        label = self.name or self.serial_number
        return (
            f"{self.serial_number} ({label})" if self.name else str(self.serial_number)
        )
