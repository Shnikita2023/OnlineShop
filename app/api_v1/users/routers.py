from fastapi import APIRouter, Depends, BackgroundTasks, Response, status
from redis.asyncio.client import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.api_v1.auth import AuthUser
from app.api_v1.auth.cookie_token_service import cookie_helper
from app.api_v1.auth.schemas import TokenInfo
from app.api_v1.auth.token_jwt_service import TokenWork
from app.api_v1.users import user_manager
from app.api_v1.users.schemas import UserCreate, UserShow, ForgotUser, ResetUser
from app.api_v1.users.utils import PasswordForgot, PasswordReset
from app.db import get_async_session
from app.db.database import get_async_redis_client

router = APIRouter(prefix="/auth",
                   tags=["Auth"])


@router.post(path="/register",
             summary="Регистрация пользователя",
             status_code=status.HTTP_201_CREATED,
             response_model=UserShow)
async def register_user(user_data: UserCreate,
                        background_tasks: BackgroundTasks,
                        session: AsyncSession = Depends(get_async_session),) -> UserShow:
    return await user_manager.create(user_data=user_data, session=session, background_tasks=background_tasks)


@router.post(path="/login",
             response_model=TokenInfo,
             summary="Аутентификация пользователя")
async def login_user(response: Response,
                     user: UserCreate = Depends(AuthUser.validate_auth_user)) -> TokenInfo:
    access_token, refresh_token = TokenWork.create_tokens(user=user, response=response)
    return TokenInfo(access_token=access_token, refresh_token=refresh_token)


@router.get(path="/logout", summary="Выход пользователя")
async def logout_user(response: Response,
                      current_user: dict = Depends(cookie_helper.get_cookie_tokens)) -> dict[str, str]:
    response.delete_cookie(cookie_helper.COOKIE_SESSION_KEY)
    return {"message": "logout successful"}


@router.get(path="/me", summary="Получение данных о пользователе")
async def auth_user_check_self_info(response: Response,
                                    user: dict = Depends(AuthUser.get_current_auth_user)) -> dict:
    return {
        "id": user["sub"],
        "username": user["username"],
        "email": user["email"]
    }


@router.post(path="/forgot_password", summary="Восстановление пароля пользователя")
async def forgot_password(forgot_data: ForgotUser,
                          session: AsyncSession = Depends(get_async_session),
                          redis_client: Redis = Depends(get_async_redis_client)) -> dict:
    return await PasswordForgot(user_email=forgot_data.email,
                                session=session,
                                redis_client=redis_client).forgot_password_user()


@router.post(path="/reset_password", summary="Сброс пароля пользователя")
async def reset_password(reset_data: ResetUser,
                         session: AsyncSession = Depends(get_async_session),
                         redis_client: Redis = Depends(get_async_redis_client)):
    return await PasswordReset(token=reset_data.token,
                               password=reset_data.password,
                               user_email=reset_data.email,
                               session=session,
                               redis_client=redis_client).reset_password_user()
