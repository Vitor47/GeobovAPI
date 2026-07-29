from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.adapters.models.base import BaseModel
from app.adapters.models.user_company import user_companies


class User(BaseModel):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    __tablename__ = "users"

    full_name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    phone = Column(String, nullable=True)
    cpf = Column(String, nullable=True)
    cnpj = Column(String, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    _password_hash = Column(String)
    is_superuser = Column(Boolean, default=False, nullable=False)

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    # Default farm used when X-Company-Id is omitted.
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    company = relationship("Company", back_populates="users")

    # Farm memberships (N:N) — source of truth for access scope.
    companies = relationship(
        "Company",
        secondary=user_companies,
        back_populates="members",
    )

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    def set_password(self, password: str) -> None:
        object.__setattr__(self, "_password_hash", self.pwd_context.hash(password))

    def authenticate(self, password: str) -> bool:
        password_hash = getattr(self, "_password_hash", None)
        if password_hash is None:
            return False
        return self.pwd_context.verify(password, str(password_hash))

    @property
    def company_ids(self) -> list[int]:
        return [company.id for company in self.companies or []]
