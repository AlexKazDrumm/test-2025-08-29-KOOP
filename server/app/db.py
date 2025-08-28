from __future__ import annotations

import datetime as dt
import enum
import os
import uuid
from typing import Literal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# postgresql+asyncpg://user:pass@host:5432/dbname  (или sqlite+aiosqlite:///./kanban.db)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./kanban.db')

Status = Literal['todo', 'in_progress', 'done']


class PriorityEnum(str, enum.Enum):
    low = 'low'
    normal = 'normal'
    high = 'high'
    urgent = 'urgent'


class EventTypeEnum(str, enum.Enum):
    created = 'created'
    updated = 'updated'
    moved = 'moved'
    deleted = 'deleted'


class Base(DeclarativeBase):
    pass


class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default='', nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='todo', nullable=False)
    priority: Mapped[PriorityEnum] = mapped_column(
        Enum(PriorityEnum), default=PriorityEnum.normal, nullable=False
    )
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: dt.datetime.now(dt.UTC),
        onupdate=lambda: dt.datetime.now(dt.UTC),
        nullable=False,
    )

    events: Mapped[list[TaskEvent]] = relationship(
        back_populates='task', cascade='all, delete-orphan'
    )


class TaskEvent(Base):
    __tablename__ = 'task_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(
        String(36), ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False
    )
    type: Mapped[EventTypeEnum] = mapped_column(Enum(EventTypeEnum), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(20))
    to_status: Mapped[str | None] = mapped_column(String(20))
    at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: dt.datetime.now(dt.UTC), nullable=False
    )

    task: Mapped[Task] = relationship(back_populates='events')


engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def next_sort_order(session: AsyncSession, status: str) -> int:
    res = await session.execute(
        select(func.coalesce(func.max(Task.sort_order), -1)).where(Task.status == status)
    )
    max_order = res.scalar_one()
    return max_order + 1


async def log_event(
    session: AsyncSession,
    task: Task,
    type_: EventTypeEnum,
    from_status: str | None = None,
    to_status: str | None = None,
):
    ev = TaskEvent(task_id=task.id, type=type_, from_status=from_status, to_status=to_status)
    session.add(ev)
