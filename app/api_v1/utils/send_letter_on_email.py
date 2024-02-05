import aiosmtplib
from email.message import EmailMessage

from pydantic import EmailStr

from app.api_v1.exceptions import HttpAPIException
from app.config import settings
from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__).init_logger


# TODO Разделить логику подключение и отправки сообщение, пока сложности с передачей контекста меденежра
class EmailSender:
    def __init__(self):
        self.smtp_hostname = settings.email.SMTP_HOST
        self.smtp_port = settings.email.SMTP_PORT
        self.smtp_user = settings.email.SMTP_USER
        self.smtp_password = settings.email.SMTP_PASSWORD

    async def send_email(self, body: str, email: EmailStr, subject: str):
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

        except aiosmtplib.SMTPAuthenticationError:
            error = "Error authenticating with SMTP server."
            raise HttpAPIException(exception=error).http_error_500

        except (aiosmtplib.SMTPServerDisconnected, aiosmtplib.SMTPConnectError):
            error = f"Error connecting to {self.smtp_hostname} on port {self.smtp_port}"
            raise HttpAPIException(exception=error).http_error_500


async def send_password_reset_email(email: EmailStr, token: str):
    url = "http://127.0.0.1:8000/auth/"
    body = f"Для сброса пароля перейдите по ссылке: {url}reset_password?token={token}"
    subject = "Сброс пароля"

    email_sender = EmailSender()
    await email_sender.send_email(body=body, email=email, subject=subject)


async def send_letter_on_after_register(email: EmailStr) -> None:
    body = ("Регистрация успешно пройдена!\n"
            "Добро пожаловать в магазин 'OnlineShop'!")
    subject = "Регистрация прошла успешно"

    email_sender = EmailSender()
    await email_sender.send_email(body=body, email=email, subject=subject)
    logger.info(f"Успешная отправка письма о регистрации на {email}")
