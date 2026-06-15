from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.adapters.models.base import BaseModel


class Company(BaseModel):
    __tablename__ = "companies"

    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    country = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    cattle = relationship(
        "Cattle", back_populates="company", cascade="all, delete-orphan"
    )
    cattle_data = relationship(
        "CattleData", back_populates="company", cascade="all, delete-orphan"
    )
    devices = relationship(
        "Device", back_populates="company", cascade="all, delete-orphan"
    )
