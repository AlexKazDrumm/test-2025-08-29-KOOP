from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Status = Literal['todo', 'in_progress', 'done']
Priority = Literal['low', 'normal', 'high', 'urgent']


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default='', max_length=5000)
    priority: Priority = 'normal'


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    status: Status | None = None
    priority: Priority | None = None


class Task(BaseModel):
    id: str
    title: str
    description: str
    status: Status
    priority: Priority
    sort_order: int
    created_at: datetime
    updated_at: datetime


class BoardState(BaseModel):
    tasks: list[Task]


class ReorderPayload(BaseModel):
    todo: list[str]
    in_progress: list[str]
    done: list[str]
