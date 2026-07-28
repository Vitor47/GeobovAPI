from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from app.adapters.models.base import BaseModel


class Role(BaseModel):
    __tablename__ = "roles"

    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="role")

    def __str__(self) -> str:
        return str(self.name)
