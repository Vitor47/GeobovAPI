from sqlalchemy import Column, ForeignKey, Integer, Table

from app.core.database import Base

user_companies = Table(
    "user_companies",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "company_id",
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
