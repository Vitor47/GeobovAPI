from app.domain.enums.role_enum import RoleEnum


class Role:
    def __init__(self, id: int, name: RoleEnum):
        self.id = id
        self.name = name
