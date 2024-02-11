#!/bin/bash

sleep 5

alembic upgrade head

celery -A app.api_v1.tasks.celery_app:celery worker --loglevel=info --pool=solo &
celery -A app.api_v1.tasks.celery_app:celery flower &
gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000


