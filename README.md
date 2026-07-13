# Dimatech API

Асинхронное REST API приложение для управления счетами и платежами.

## Стек

- Python 3.12 + Sanic
- PostgreSQL 16
- SQLAlchemy (async)
- Docker Compose

## Тестовые учетные данные (создаются при миграции)

| Роль | Email | Password |
|------|-------|----------|
| Пользователь | user@example.com | user123 |
| Администратор | admin@example.com | admin123 |

## Запуск с Docker Compose

```bash
docker compose up --build
```

Приложение будет доступно на `http://localhost:8000`.

## Запуск без Docker Compose

### Требования

- PostgreSQL (запущенный на localhost:5432)
- Python 3.12+
- pip

### Установка

```bash
# 1. Создать базу данных
createdb dimatech

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Настроить .env (или использовать переменные окружения)
cp .env_example .env
cp alembic.ini_example alembic.ini
# Отредактировать DATABASE_URL при необходимости или задайте переменные окружения другим способом

# 4. Запустить приложение
python -m app.main
```

База данных и таблицы создаются автоматически при запуске приложения (через `Base.metadata.create_all`).

## API Endpoints

### Авторизация

- `POST /api/v1/auth/login` — авторизация (email, password) → token

### Пользователь (требуется JWT)

- `GET /api/v1/users/me` — данные пользователя
- `GET /api/v1/users/me/accounts` — список счетов с балансами
- `GET /api/v1/users/me/payments` — список платежей

### Администратор (требуется JWT с правами admin)

- `GET /api/v1/admin/users` — список пользователей
- `POST /api/v1/admin/users` — создание пользователя
- `PUT /api/v1/admin/users/<id>` — обновление пользователя
- `DELETE /api/v1/admin/users/<id>` — удаление пользователя
- `GET /api/v1/admin/users/<id>/accounts` — счета пользователя

### Вебхук платежной системы

- `POST /api/v1/webhook/payment` — обработка платежа

### Пример запроса вебхука

```json
{
  "transaction_id": "5eae174f-7cd0-472c-bd36-35660f00132b",
  "user_id": 1,
  "account_id": 1,
  "amount": 100,
  "signature": "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"
}
```

### Пример авторизации

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "user123"}'
```

Ответ:
```json
{"token": "eyJ...", "user": {"id": 1, "email": "user@example.com", ...}}
```

Использование токена:
```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJ..."
```
