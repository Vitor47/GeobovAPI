from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.adapters.models.base import BaseModel
from app.domain.enums.cattle_enum import GenderEnum


class Cattle(BaseModel):
    __tablename__ = "cattle"

    tag = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    birth_date = Column(DateTime(timezone=True), nullable=True)
    weight = Column(Float, nullable=True)
    breed = Column(String, nullable=True)
    gender: Mapped[GenderEnum | None] = mapped_column(
        Enum(GenderEnum, name="gender_enum"),
        nullable=True,
    )
    color = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="cattle")
    device = relationship("Device", back_populates="cattle", uselist=False)

    def __str__(self) -> str:
        return f"{self.tag} — {self.name}"
