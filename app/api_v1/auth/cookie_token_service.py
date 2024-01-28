import json
from datetime import datetime, timedelta

from fastapi import Cookie, Response

from app.api_v1.exceptions import CustomException
from app.config import settings


class CookieTokenHelper:
    """
    Класс для работы с куками для токена
    """

    COOKIE_SESSION_KEY: str = settings.session_cookie.COOKIE_SESSION_KEY
    COOKIE_SESSION_TIME: int = settings.session_cookie.COOKIE_SESSION_TIME

    @classmethod
    def get_cookie_tokens(cls, cookie_tokens: str = Cookie(alias=COOKIE_SESSION_KEY, default=None)) -> str:
        if cookie_tokens:
            return cookie_tokens
        raise CustomException(exception="invalid cookie").http_error_401

    @classmethod
    def create_cookie_for_tokens(cls,
                                 response: Response,
                                 access_token: str,
                                 refresh_token: str) -> None:
        expires = datetime.utcnow() + timedelta(minutes=cls.COOKIE_SESSION_TIME)
        expires_cookie = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        tokens = {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
        json_data_token = json.dumps(tokens)
        response.set_cookie(cls.COOKIE_SESSION_KEY,
                            json_data_token,
                            expires=expires_cookie,
                            httponly=True)

    @staticmethod
    def parsing_cookie_tokens(cookie_tokens: str) -> tuple:
        tokens_dict = json.loads(cookie_tokens)
        return tokens_dict["access_token"], tokens_dict["refresh_token"]


cookie_helper = CookieTokenHelper()
