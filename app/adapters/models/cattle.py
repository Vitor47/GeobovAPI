from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Cattle(Base):
    __tablename__ = "cattle"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="cattle")
    data = relationship("CattleData", back_populates="cattle")
    device = relationship("Device", back_populates="cattle", uselist=False)


class CattleData(Base):
    __tablename__ = "cattle_data"

    id = Column(Integer, primary_key=True, index=True)

    cattle_id = Column(
        Integer,
        ForeignKey("cattle.id", ondelete="CASCADE"),
        nullable=False,
    )

    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    movement = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)

    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    cattle = relationship("Cattle", back_populates="data")
    company_id = Column(Integer, ForeignKey("companies.id"))
    company = relationship("Company", back_populates="cattle_data")
