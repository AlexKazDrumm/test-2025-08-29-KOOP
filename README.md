````md
# Kanban board — FastAPI + PostgreSQL + WebSocket + Vue 3 (TypeScript)

Канбан-доска (To Do / In Progress / Done) с real-time синхронизацией, drag-and-drop и хранением в **PostgreSQL** (async драйвер `asyncpg`).

## Стек
- **Backend:** FastAPI (async), SQLAlchemy 2.0 (async) + PostgreSQL (`asyncpg`), WebSocket
- **Frontend:** Vue 3 (Composition API, TypeScript), Vite
- **Dev:** Docker (Postgres + API + Web), docker-compose

## Быстрый старт (Docker)
```bash
docker compose up --build
# UI:  http://localhost:5173
# API: http://localhost:8000
# DB:  localhost:5432  (user=postgres, password=postgres, db=kanban)
````

* API берёт строку подключения из `DATABASE_URL` (см. `docker-compose.yml`).
* При старте создаются таблицы (`init_db()` в `server/app/db.py`).

## Локальный запуск без Docker

### PostgreSQL

Поднимите Postgres 16+, создайте БД `kanban` и пользователя, либо используйте дефолт `postgres:postgres`.

### Backend

```bash
cd server
python -m venv .venv && . .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Пример строки подключения:
# bash/zsh:   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/kanban"
# PowerShell: $env:DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/kanban"
python uvicorn_config.py
```

### Frontend

```bash
cd client
npm i
# (опционально) VITE_API_URL=http://localhost:8000
npm run dev
# UI: http://localhost:5173
```

## Конфигурация

* `DATABASE_URL` — строка подключения SQLAlchemy:

  * PostgreSQL: `postgresql+asyncpg://user:pass@host:5432/kanban`
  * SQLite (локально): `sqlite+aiosqlite:///./kanban.db`
* `VITE_API_URL` — базовый URL API для фронтенда (по умолчанию `http://localhost:8000`).