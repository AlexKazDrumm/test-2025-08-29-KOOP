# Kanban-доска с синхронизацией в реальном времени

Kanban-приложение на FastAPI и Vue с общей доской для всех подключённых
клиентов.

## Возможности

- колонки To Do, In Progress и Done;
- создание, редактирование и удаление карточек;
- drag-and-drop внутри колонок и между ними;
- сохранение порядка карточек;
- синхронизация через WebSocket;
- восстановление состояния после переподключения;
- REST API для операций с доской.

## Стек

- Vue 3, TypeScript, Vite;
- FastAPI, async SQLAlchemy, WebSocket;
- PostgreSQL;
- Docker Compose.

## Запуск

```bash
docker compose up --build
```

- приложение: http://localhost:5173
- API: http://localhost:8000

## Локальная разработка

Backend:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r server/requirements.txt
python server/uvicorn_config.py
```

Frontend:

```powershell
Set-Location client
npm ci
npm run dev
```

## Проверка

```powershell
Set-Location client
npm run lint
npm run build
```

## Документация

Исходные требования приведены в [TASK.md](TASK.md).
