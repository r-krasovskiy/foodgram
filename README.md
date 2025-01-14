![Build Status](https://github.com/r-krasovskiy/foodgram/actions/workflows/main.yml/badge.svg)

# Foodgram

## Описание проекта
**Foodgram** — это сайт, на котором пользователи будут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.
Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Функциональные возможности
- Регистрация и авторизация пользователей.
- Публикация рецептов пользователями: загрузка изображений, описания, списка ингридиентов.
- Добавление рецепотов в избранное и подписка на авторов рецептов.
- Формирование списка покупок на основе ингридиентов и его выгрузка в txt-файл.
- Админ-зона для управления контентом (фильтрация, скрытие, публикация и пр.)
- Предоставление данных через API.

## Стек технологий
- **Backend**: Python, Django, Django REST Framework, Gunicorn
- **Frontend**: React, JavaScript
- **База данных**: PostgreSQL
- **Сервер**: Nginx
- **Docker**: Docker, Docker Compose
- **DevOps**: GitHub Actions, DockerHub

## Локальное развертывание
### 1. Клонируйте репозиторий
```bash
git clone https://github.com/r-krasovskiy/foodgram.git
cd foodgram
```

### 2. Запустите фронтенд
```bash
cd frontend
npm i
npm run start
```

### 3. Запустите бэкенд (строго в новом терминале)
```bash
cd backend
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 4. Добавьте готовую базу ингрилиентов и тэгов для рецептов (опционально)
```bash
python manage.py import_ingredients
python manage.py import_tags
```

### 5. Создайте суперпользователя для управления админ-зоной:
```bash
python manage.py createsuperuser
```

## Развертывние на серере
### 1. Клонируйте репозиторий
```bash
git clone https://github.com/r-krasovskiy/foodgram.git
cd foodgram
```

### 2. Заполните переменные окружения
Создайте файл `.env` в корневой директории и добавьте туда следующие переменные (пример заполнения - в файле `env.example`):
- `POSTGRES_DB`- имя вашей базы данных, которая создается при инициализации контейнера с PostgreSQL (наприме, foodgram).
- `POSTGRES_USER` - имя пользователя вашей базы данных (например, foodgram_user).
- `POSTGRES_PASSWORD` - пароль от вашей базы данных (например, foodgram_password).
- `DB_NAME` - имя вашей базы данных,  к которой нужно подключаться; приложение будет использовать это имя для установления соединения с базой данных (например, foodgram).
- `DB_HOST` - хост (например, db)
- `DB_PORT`- порт (например, 5432)
- `ALLOWED_HOSTS` - адрес хоста и адрес приложения в Интернете, создавнный вами (например, foodgram.ddnsfree.com)
- `DEBUG` - режим отладки приложения (True - для отладки, False - для продакшена).
- `SECRET_KEY` - ключ безопасности приложения (генерация токенов, безопасность сессий).


### 3. Соберите и запустите контейнеры
При разработке используйте:
```bash
docker-compose up --build
```
При продакшене используйте:
```bash
docker-compose.production.yml up --build
```

### 4. Для развертывания DevOps-процессов на GitHub Actions (опционально)
Автоматическое развертывание на удаленном сервере в продакшене после коммита изменений в ветку `main` описывает файл `main.yml`, а также послылает в 
Telegram сообщение об успешном деплойменте в продакшен после его завершения. Требует предвариательного создания Telegram-бота через `@BotFather`.
В настройках секретов репозитория с приложением (Settings -> Secrets and variables -> Actions) создайте следующие переменные:
- `DOCKER_USERNAME` - имя пользователя на DockerHub.
- `DOCKER_PASSWORD` - пароль пользователя на DockerHub.
- `HOST` - IP-адрес удаленного сервера (хоста).
- `SSH_KEY` - ключ SSH-доступа к удаленному серверу.
- `USER` - логин SSH-доступа к удаленному серверу.
- `SSH_PASSPHRASE` - пароль SSH-доступа к удаленному серверу.
- `TELEGRAM_TO` - ID телеграм-аккаунта, куда необходимо посылать сообщения об успешном деплойменте (узнать свой ID можно у телеграм-бота `@userinfobot`).
- `TELEGRAM_TOKEN` - токен Telegram-бота (получить можно у `@BotFather` при создании бота в Telegram).


## Пример развернутого проекта
https://foodgram.ddnsfree.com/

#### Автор
Roman Krasowski
