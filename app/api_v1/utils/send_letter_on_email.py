import smtplib

from email.message import EmailMessage
from pydantic import EmailStr

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.tasks.celery_app import celery
from app.config import settings
from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__).init


# TODO Разделить логику подключение и отправки сообщение, пока сложности с передачей контекста меденежра
class EmailSender:
    def __init__(self):
        self.smtp_hostname = settings.email.SMTP_HOST
        self.smtp_port = settings.email.SMTP_PORT
        self.smtp_user = settings.email.SMTP_USER
        self.smtp_password = settings.email.SMTP_PASSWORD

    def send_email(self, body: str, email: EmailStr, subject: str):
        try:
            with smtplib.SMTP_SSL(self.smtp_hostname, self.smtp_port) as smtp:
                smtp.login(self.smtp_user, self.smtp_password)
                message = EmailMessage()
                message["From"] = self.smtp_user
                message["To"] = email
                message["Subject"] = subject
                message.set_content(body)
                smtp.send_message(message)

        except smtplib.SMTPAuthenticationError:
            error = "Error authenticating with SMTP server."
            raise HttpAPIException(exception=error).http_error_500

        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError):
            error = f"Error connecting to {self.smtp_hostname} on port {self.smtp_port}"
            raise HttpAPIException(exception=error).http_error_500


@celery.task
def send_password_reset_email(email: EmailStr, token: str):
    url = "http://127.0.0.1:8000/auth/"
    body = f"Для сброса пароля перейдите по ссылке: {url}reset_password?token={token}"
    subject = "Сброс пароля"

    email_sender = EmailSender()
    email_sender.send_email(body=body, email=email, subject=subject)


@celery.task
def send_letter_on_after_register(email: EmailStr) -> None:
    body = ("Регистрация успешно пройдена!\n"
            "Добро пожаловать в магазин 'OnlineShop'!")
    subject = "Регистрация прошла успешно"

    email_sender = EmailSender()
    email_sender.send_email(body=body, email=email, subject=subject)
