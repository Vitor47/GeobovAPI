from sqlalchemy.orm import Session

from app.adapters.models.role import Role
from app.adapters.models.user import User
from app.domain.repositories.user_repository_abstract import (
    UserRepositoryAbstract,
)


class UserRepository(UserRepositoryAbstract):

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, data):
        role = self.db.query(Role).filter(Role.name == data.role.value).first()

        db_user = User(
            full_name=data.full_name,
            birth_date=data.birth_date,
            email=data.email,
            company_id=data.company_id,
            role=role,
        )

        db_user.set_password(data.password)

        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str):
        return self.db.query(User).filter(User.email == email).first()

    def delete_user(self, user_id: int):
        user = self.get_user_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
