import aiosmtplib
from email.message import EmailMessage

from pydantic import EmailStr

from app.api_v1.exceptions import HttpAPIException
from app.api_v1.pages.views import get_discount_page
from app.api_v1.products import Product
from app.api_v1.products.services import product_service
from app.api_v1.users.database import user_db
from app.config import settings
from app.db import async_session_maker
from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__).init_logger


class EmailSender:
    def __init__(self):
        self.smtp_hostname = settings.email.SMTP_HOST
        self.smtp_port = settings.email.SMTP_PORT
        self.smtp_user = settings.email.SMTP_USER
        self.smtp_password = settings.email.SMTP_PASSWORD
        self.smtp = None

    async def connect_smtp(self):
        """Подключение к серверу SMTP"""
        try:
            self.smtp = aiosmtplib.SMTP(hostname=self.smtp_hostname,
                                        port=self.smtp_port,
                                        use_tls=True)
            await self.smtp.connect()
            await self.smtp.login(self.smtp_user, self.smtp_password)
            return self.smtp

        except aiosmtplib.SMTPAuthenticationError:
            error = "Error authenticating with SMTP server."
            raise HttpAPIException(exception=error).http_error_500

        except (aiosmtplib.SMTPServerDisconnected, aiosmtplib.SMTPConnectError):
            error = f"Error connecting to {self.smtp_hostname} on port {self.smtp_port}"
            raise HttpAPIException(exception=error).http_error_500

    async def send_notification(self, body: str, email: EmailStr, subject: str):
        try:
            message = EmailMessage()
            message["From"] = settings.email.SMTP_USER
            message["To"] = email
            message["Subject"] = subject
            message.add_alternative(body, subtype='html')
            await self.smtp.send_message(message)

        except aiosmtplib.SMTPServerDisconnected:
            error = f"Error connecting to {self.smtp_hostname} on port {self.smtp_port}"
            raise HttpAPIException(exception=error).http_error_500


async def send_password_reset_email(email: EmailStr, token: str) -> None:
    """Отправка сообщение о сбросе пароля"""
    url = "http://127.0.0.1:8000/auth/"
    body = f"Для сброса пароля перейдите по ссылке: {url}reset_password?token={token}"
    subject = "Сброс пароля"

    email_sender = EmailSender()
    async with await email_sender.connect_smtp():
        await email_sender.send_notification(body=body, email=email, subject=subject)
        logger.info(f"Успешная отправка письма о сбросе пароля на {email}")


async def send_letter_on_after_register(email: EmailStr) -> None:
    """Отправка сообщение об успешной регистрации"""
    body = ("Регистрация успешно пройдена!\n"
            "Добро пожаловать в магазин 'OnlineShop'!")
    subject = "Регистрация прошла успешно"

    email_sender = EmailSender()
    async with await email_sender.connect_smtp():
        await email_sender.send_notification(body=body, email=email, subject=subject)
        logger.info(f"Успешная отправка письма о регистрации на {email}")


async def send_to_discount_products_emails() -> None:
    """Отправка сообщений пользователям о скидках товаров"""
    subject = "Скидки на товары"
    users_emails, name_and_price_products = await preparation_by_discount_products()

    if users_emails and name_and_price_products:
        body = await get_discount_page(products_discount=name_and_price_products)
        email_sender = EmailSender()
        async with await email_sender.connect_smtp():
            for email in users_emails:
                await email_sender.send_notification(body=body, email=email, subject=subject)
                logger.info(f"Успешная отправка письма о скидках товаров на {email}")


async def preparation_by_discount_products() -> tuple[list, list]:
    """Получение продуктов по скидки и emails пользователей"""
    async with async_session_maker() as session:
        products: list[Product] = await product_service.get_products_only_discount(session=session)
        users_emails: list[str] = await user_db.get_emails_users(session=session)
        name_and_price_products: list[dict] = [{product.name: product.price} for product in products]
        return users_emails, name_and_price_products
