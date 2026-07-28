from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.adapters.database.session_factory import SessionFactory
from app.adapters.models.user import User


class AdminAuth(AuthenticationBackend):
    """
    Restrict SQLAdmin to active superusers authenticated by email/password.

    Session stores the user id; each request re-validates is_superuser in the DB.
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = str(form.get("username") or "").strip().lower()
        password = str(form.get("password") or "")

        if not email or not password:
            return False

        db = SessionFactory.create()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user is None:
                return False
            if not user.is_superuser:
                return False
            if not user.authenticate(password):
                return False

            request.session.update(
                {
                    "admin_user_id": user.id,
                    "admin_email": user.email,
                }
            )
            return True
        finally:
            db.close()

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if user_id is None:
            return False

        db = SessionFactory.create()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user is None or not user.is_superuser:
                request.session.clear()
                return False
            return True
        finally:
            db.close()
