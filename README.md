# Cервис Online Shop

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/-FastAPI-464646?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Асинхронность](https://img.shields.io/badge/-Асинхронность-464646?style=flat-square&logo=Асинхронность)]()
[![Cookies](https://img.shields.io/badge/-Cookies-464646?style=flat-square&logo=Cookies)]()
[![JWT](https://img.shields.io/badge/-JWT-464646?style=flat-square&logo=JWT)]()
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Alembic](https://img.shields.io/badge/-Alembic-464646?style=flat-square&logo=Alembic)](https://alembic.sqlalchemy.org/en/latest/)
[![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-464646?style=flat-square&logo=SQLAlchemy)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Redis](https://img.shields.io/badge/-Redis-464646?style=flat-square&logo=Redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/-Celery-464646?style=flat-square&logo=Celery)](https://docs.celeryq.dev/en/stable/)
[![Sentry](https://img.shields.io/badge/-Sentry-464646?style=flat-square&logo=Sentry)](https://sentry.io/welcome/)
[![Prometheus](https://img.shields.io/badge/-Prometheus-464646?style=flat-square&logo=Prometheus)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/-Grafana-464646?style=flat-square&logo=Grafana)](https://grafana.com/)
[![Nginx](https://img.shields.io/badge/-Nginx-009639?style=flat-square&logo=Nginx)](https://www.nginx.com/)
[![Uvicorn](https://img.shields.io/badge/-Uvicorn-464646?style=flat-square&logo=uvicorn)](https://www.uvicorn.org/)
[![Gunicorn](https://img.shields.io/badge/-Gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)

### Описание проекта:
Данное приложение можно использовать в качестве Интернет-магазина, для различного продукта

Функционал приложение:
- JWT авторизация, аутентификация.
- Регистрация пользователя, восстановление пароля.
- У не аутентифицированных пользователей доступ к API только на уровне чтения.
- Создание объектов разрешено только аутентифицированным пользователям.
- Возможность получения подробной информации о себе.
- Загрузка тестовых данных в БД.
- CRUD профиля.
- CRUD категорий.
- CRUD корзины пользователя.
- CRUD заказов пользователя.
- CRUD продуктов.
- Отправка писем на Email.
- Возможность администрирования сервиса.
- Версионирование API.
- Кеширование/брокер задач с помощью Redis.
- Анализ и сбор метрик (Grafana, Prometheus).
- Использование балансировщика, прокси сервера Nginx.
- Логирование посредством кастомного логгера.
- Мониторинг ошибок с помощью Sentry.
- Возможность развернуть проект в Docker-контейнерах.

## To Do:

- Внедрить UI пользователя с помощью библиотеки React (на стадии разработки)
- Покрыть больше кода тестами
- Расширить функционал приложение
- Добавить более длительную задачу для Celery (в проект уже инициализирован)
- Реализовать отдельную сущность с балансом и транзакций пользователя
- Развернуть CI/CD на платформе GitLab

### Инструменты разработки

**Стек:**
- Python >= 3.11
- FastAPI == 0.104.1
- PostgreSQL == 16.1
- Docker == 20.14.24
- Redis == 7.2.3
- Alembic == 1.13.1
- SQLAlchemy == 2.0.25
- SQLAdmin == 0.16.0
- Celery == 5.3.6
- Flower == 2.0.1
- Sentry == 1.40.1
- Nginx == 1.25.3
- Grafana == 10.3.1
- Prometheus == 2.49

## Разработка

##### 1) Клонировать репозиторий

    git clone ссылка_сгенерированная_в_вашем_репозитории

##### 2) Установить poetry на компьютер

    https://python-poetry.org/docs/#installation

##### 3) Активировать виртуальное окружение и установить зависимости

        poetry install

##### 6) Переименовать файл .env.example на .env и изменить на свои данные

##### 7) Установить docker на свою ОС

    https://docs.docker.com/engine/install/

##### 8) В корневом каталоге проекта, создать папку certs и сгенерировать себе ключи

    # Generate an RSA private key, of sizw 2048
    openssl genrsa -out jwt-private.pem 2048

    # Extract the publick key from the key pair, which can be used in a certificate
    openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem

##### 9) Запустить контейнеры через docker

    docker-compose up -d

##### 10) Перейти в документацию api

    127.0.0.1:8000/api/docs

## Дополнительные шаги для запуска сторонних библиотек:

##### 1) Открытие админ панели для взаимодействия с БД, перед этим зарегистрировать пользователя с is_superuser=True

    127.0.0.1:8000/admin

##### 2) Открытие Flower для взаимодействия с Celery

    127.0.0.1:5555

##### 3) Для работы с Sentry, нужна зарегистрироваться на их платформе, создать проект и скопировать SENTRY_DSN в .env

    https://www.sentry.dev/for/python/

##### 4) Для запуска Prometheus

    127.0.0.1:9090

##### 5) Для отображения метрик в красивом стиле, нужна Grafanа

    127.0.0.1:3000

##### 6) Перед созданием дашбордов, нужна подключить источник в Connections - Data Sources - Prometheus

       Prometheus server URL: http://prometheus_shop:9090




