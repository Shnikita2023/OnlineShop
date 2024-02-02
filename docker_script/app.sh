#!/bin/bash

sleep 5
alembic upgrade head
#gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000