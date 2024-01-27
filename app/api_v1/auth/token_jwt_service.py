from datetime import datetime, timedelta

import jwt
from fastapi import Cookie, Depends
from jwt import InvalidTokenError
from pydantic import BaseModel

from app.api_v1.exceptions import CustomException
from app.api_v1.users.schemas import UserShow
from app.config import settings


class TokenInfo(BaseModel):
    access_token: str
    token_type: str = "Bearer"


class TokenService:

    @staticmethod
    def encode_jwt(
            payload: dict,
            private_key: str = settings.auth_jwt.private_key.read_text(),
            algorithm: str = settings.auth_jwt.algorithm,
            expire_minutes: int = settings.auth_jwt.access_token_expire_minute
    ):
        to_encode = payload.copy()
        now_time = datetime.utcnow()
        expire_token = now_time + timedelta(minutes=expire_minutes)
        to_encode.update(exp=expire_token, iat=now_time)

        encoded = jwt.encode(payload=to_encode, key=private_key, algorithm=algorithm)
        return encoded

    @staticmethod
    def decode_jwt(
            token: bytes | str,
            public_key: str = settings.auth_jwt.public_key.read_text(),
            algorithm: str = settings.auth_jwt.algorithm
    ):
        decoded = jwt.decode(jwt=token, key=public_key, algorithms=[algorithm])
        return decoded


class TokenWork(TokenService):
    COOKIE_SESSION_KEY: str = settings.session_cookie.COOKIE_SESSION_KEY
    COOKIE_SESSION_TIME: int = settings.session_cookie.COOKIE_SESSION_TIME

    @staticmethod
    def get_token_data(token_jwt: str = Cookie(alias=COOKIE_SESSION_KEY, default=None)) -> str:
        if token_jwt:
            return token_jwt
        raise CustomException(exception="invalid cookie").http_error_401

    @classmethod
    def get_current_token_payload(cls, token: str = Depends(get_token_data)) -> UserShow:
        try:
            return cls.decode_jwt(token=token)
        except InvalidTokenError:
            raise CustomException(exception="invalid cookie").http_error_401
