import aiosmtplib

from email.message import EmailMessage
from aiosmtplib import SMTPConnectError
from pydantic import EmailStr

from app.api_v1.exceptions import HttpAPIException
from app.config import settings


async def connect_smtp(body: str, email: EmailStr, subject: str) -> None:
    try:
        async with aiosmtplib.SMTP(hostname=settings.email.SMTP_HOST,
                                   port=settings.email.SMTP_PORT,
                                   use_tls=True) as smtp:
            await smtp.login(settings.email.SMTP_USER, settings.email.SMTP_PASSWORD)
            message = EmailMessage()
            message["From"] = settings.email.SMTP_USER
            message["To"] = email
            message["Subject"] = subject
            message.set_content(body)
            await smtp.send_message(message)

    except SMTPConnectError:
        error = f"Error connecting to {settings.email.SMTP_HOST} on port {settings.email.SMTP_PORT}"
        raise HttpAPIException(exception=error).http_error_500


async def send_letter_on_after_register(email: EmailStr) -> None:
    try:
        body = ("Регистрация успешно пройдена!\n"
                "Добро пожаловать в магазин 'OnlineShop'!")
        subject = "Регистрация прошла успешно"
        await connect_smtp(body=body, email=email, subject=subject)

    except Exception:
        raise HttpAPIException(exception="Ошибка отправки письма").http_error_500


async def send_password_reset_email(email: EmailStr, token: str):
    try:
        url = "http://127.0.0.1:8000/auth/"
        body = f"Для сброса пароля перейдите по ссылке: {url}reset_password?token={token}"
        subject = "Сброс пароля"
        await connect_smtp(body=body, email=email, subject=subject)

    except Exception:
        raise HttpAPIException(exception="Ошибка отправки письма").http_error_500
