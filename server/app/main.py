from __future__ import annotations
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .db import EventTypeEnum, SessionLocal, Task, init_db, log_event, next_sort_order
from .schemas import ReorderPayload, TaskCreate, TaskUpdate
from .schemas import Task as TaskDTO
from .ws import ws_manager

app = FastAPI(title='Kanban API (PostgreSQL-ready)')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@app.on_event('startup')
async def on_startup():
    await init_db()


@app.get('/tasks', response_model=list[TaskDTO])
async def list_tasks(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Task))
    rows = res.scalars().all()
    return [
        TaskDTO(
            **{
                'id': r.id,
                'title': r.title,
                'description': r.description,
                'status': r.status,
                'priority': r.priority.value if hasattr(r.priority, 'value') else r.priority,
                'sort_order': r.sort_order,
                'created_at': r.created_at,
                'updated_at': r.updated_at,
            }
        )
        for r in rows
    ]


@app.post('/tasks', response_model=TaskDTO, status_code=201)
async def create_task(payload: TaskCreate, session: AsyncSession = Depends(get_session)):
    order = await next_sort_order(session, 'todo')
    t = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        sort_order=order,
    )
    session.add(t)
    await session.flush()
    await log_event(session, t, EventTypeEnum.created, None, t.status)
    await session.commit()
    await session.refresh(t)
    dto = TaskDTO(
        id=t.id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority.value if hasattr(t.priority, 'value') else t.priority,
        sort_order=t.sort_order,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )
    await ws_manager.broadcast({'type': 'created', 'task': dto.model_dump(mode='json')})
    return dto


@app.patch('/tasks/{task_id}', response_model=TaskDTO)
async def update_task(
    task_id: str, payload: TaskUpdate, session: AsyncSession = Depends(get_session)
):
    res = await session.execute(select(Task).where(Task.id == task_id))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail='Task not found')

    from_status = t.status
    changed_status = False

    if payload.title is not None:
        t.title = payload.title
    if payload.description is not None:
        t.description = payload.description
    if payload.priority is not None:
        t.priority = payload.priority
    if payload.status is not None and payload.status != t.status:
        t.status = payload.status
        t.sort_order = await next_sort_order(session, t.status)
        changed_status = True

    await session.flush()

    await log_event(
        session,
        t,
        EventTypeEnum.moved if changed_status else EventTypeEnum.updated,
        from_status if changed_status else None,
        t.status if changed_status else None,
    )

    await session.commit()
    await session.refresh(t)
    dto = TaskDTO(
        id=t.id,
        title=t.title,
        description=t.description,
        status=t.status,
        priority=t.priority.value if hasattr(t.priority, 'value') else t.priority,
        sort_order=t.sort_order,
        created_at=t.created_at,
        updated_at=t.updated_at,
    )
    await ws_manager.broadcast({'type': 'updated', 'task': dto.model_dump(mode='json')})
    return dto


@app.delete('/tasks/{task_id}', status_code=204)
async def delete_task(task_id: str, session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Task).where(Task.id == task_id))
    t = res.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail='Task not found')
    await log_event(session, t, EventTypeEnum.deleted, t.status, None)
    await session.delete(t)
    await session.commit()
    await ws_manager.broadcast({'type': 'deleted', 'task_id': task_id})
    return


@app.post('/tasks/reorder', status_code=204)
async def reorder(payload: ReorderPayload, session: AsyncSession = Depends(get_session)):
    # назначаем sort_order по спискам
    for status, ids in (
        ('todo', payload.todo),
        ('in_progress', payload.in_progress),
        ('done', payload.done),
    ):
        for order, id_ in enumerate(ids):
            res = await session.execute(select(Task).where(Task.id == id_))
            t = res.scalar_one_or_none()
            if not t:
                continue
            t.status = status
            t.sort_order = order
    await session.commit()
    res = await session.execute(select(Task))
    rows = res.scalars().all()
    state = {
        'type': 'snapshot',
        'state': {
            'tasks': [
                TaskDTO(
                    id=r.id,
                    title=r.title,
                    description=r.description,
                    status=r.status,
                    priority=r.priority.value if hasattr(r.priority, 'value') else r.priority,
                    sort_order=r.sort_order,
                    created_at=r.created_at,
                    updated_at=r.updated_at,
                ).model_dump(mode='json')
                for r in rows
            ]
        },
    }
    await ws_manager.broadcast(state)
    return


@app.websocket('/ws')
async def ws_board(ws: WebSocket, session: AsyncSession = Depends(get_session)):
    await ws_manager.connect(ws)
    try:
        res = await session.execute(select(Task))
        rows = res.scalars().all()
        await ws.send_json(
            {
                'type': 'snapshot',
                'state': {
                    'tasks': [
                        TaskDTO(
                            id=r.id,
                            title=r.title,
                            description=r.description,
                            status=r.status,
                            priority=r.priority.value
                            if hasattr(r.priority, 'value')
                            else r.priority,
                            sort_order=r.sort_order,
                            created_at=r.created_at,
                            updated_at=r.updated_at,
                        ).model_dump(mode='json')
                        for r in rows
                    ]
                },
            }
        )
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)
    except Exception:
        await ws_manager.disconnect(ws)
