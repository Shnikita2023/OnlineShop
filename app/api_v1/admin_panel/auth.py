from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.api_v1.auth import AuthUser
from app.api_v1.auth.token_jwt_service import TokenService
from app.api_v1.users.models import User
from app.db import async_session_maker


class AdminAuth(AuthenticationBackend):
    """
    Класс для создания аутентификации в админ панели
    """

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
        try:
            async with async_session_maker() as session:
                user: User = await AuthUser.validate_auth_user(session=session, email=email, password=password)

            if user.is_superuser is True:
                access_jwt_payload = {
                    "sub": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser
                }
                access_token = TokenService.encode_jwt(payload=access_jwt_payload)
                request.session.update({"token": access_token})

                return True

        except Exception:
            pass

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return False

        payload_user = TokenService.decode_jwt(token=token)

        if payload_user:
            return True


authentication_backend = AdminAuth(secret_key="...")
