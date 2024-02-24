from fastapi import APIRouter, BackgroundTasks

from app.api_v1.utils.send_letter_on_email import send_to_discount_products_emails


router = APIRouter(
    prefix="/send-notification",
    tags=["Notifications"]
)


@router.get(path="/",
            summary="Отправка скидок на товары пользователям")
async def create_order(background_tasks: BackgroundTasks) -> dict[str, str]:
    background_tasks.add_task(send_to_discount_products_emails)
    return {"message": "Товары со скидками отправлены на email пользователям"}


