from app.core.database import SessionLocal


class SessionFactory:

    @staticmethod
    def create():
        return SessionLocal()
