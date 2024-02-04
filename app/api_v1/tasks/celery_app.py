from celery import Celery

from app.config import settings

celery = Celery(__name__,
                broker=settings.celery.CELERY_BROKER_URL,
                backend=settings.celery.CELERY_RESULT_BACKEND)
