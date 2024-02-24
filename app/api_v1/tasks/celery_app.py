from datetime import timedelta

from celery import Celery

from app.config import settings
from app.logging_config import MyLogger

logger = MyLogger(pathname=__name__,
                  name_logger="celery",
                  filename="celery.log").init_logger

celery = Celery(__name__,
                broker=settings.celery.CELERY_BROKER_URL,
                backend=settings.celery.CELERY_RESULT_BACKEND,
                )

celery.conf.update(
    result_expires=timedelta(hours=1),
    broker_transport_options={"visibility_timeout": 3600},
)
