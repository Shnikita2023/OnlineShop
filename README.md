<h2 align="center">Online Shop</h2>


### Описание проекта:

Веб-приложение интернет-магазина.
- JWT авторизация, аутентификация
- Регистрация пользователя, восстановление пароля
- Админ панель для более удобного взаимодействия с БД
- CRUD профиля
- CRUD категорий
- CRUD корзины пользователя
- CRUD заказов пользователя
- CRUD продуктов
- Отправка писем на Email


## To Do:

- Внедрить UI пользователя с помощью библиотеки React (на стадии разработки)
- Покрыть больше кода тестами
- Расширить функционал приложение
- Добавить более длительную задачу для Celery (в проект уже инициализирован)
- Внедрить визуализацию метрик, ошибок, логов через Grafana/Prometheus
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





