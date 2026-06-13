from datetime import date

from app.domain.entities.role import Role


class User:
    def __init__(
        self,
        id: int,
        full_name: str,
        birth_date: date,
        email: str,
        password_hash: str,
        company_id: int,
        role: Role,
    ):
        self.id = id
        self.full_name = full_name
        self.birth_date = birth_date
        self.email = email
        self.password_hash = password_hash
        self.company_id = company_id
        self.role = role
