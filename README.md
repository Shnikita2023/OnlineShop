<h2 align="center">Online Shop</h2>


### Описание проекта:
Веб-приложение интернет-магазина.
- JWT авторизация, аутентификация
- Регистрация пользователя, восстановление пароля
- CRUD профиля
- CRUD категорий
- CRUD корзины пользователя
- CRUD заказов пользователя
- CRUD продуктов
- Отправка Email

## To Do:
- Разработать UI пользователя на React

### Инструменты разработки

**Стек:**
- Python >= 3.11
- FastAPI == 0.104.1
- PostgreSQL
- Docker
- Redis
- Alembic
- SQLAlchemy

## Разработка

##### 2) Клонировать репозиторий

    git clone ссылка_сгенерированная_в_вашем_репозитории

##### 3) Установить poetry на компьютер


##### 4) Активировать виртуальное окружение и установить зависимости

        poetry install

##### 6) Переименовать файл .env.example на .env и изменить на свои данные

##### 7) Установить docker на свою ОС

##### 8) В корневом каталоге проекта, создать папку certs и сгенерировать себе ключи
    # Generate an RSA private key, of sizw 2048
    openssl genrsa -out jwt-private.pem 2048

    # Extract the publick key from the key pair, which can be used in a certificate
    openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem

##### 9) Запустить контейнеры с базами данными через docker

    docker-compose up -d

##### 10) Запустить сервер uvicorn 

    uvicorn app.main:app --reload





