from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum

def get_current_time():
    return datetime.now(timezone.utc)

class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: bool = Field(default=False)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_completed: Optional[bool] = None
    priority: Optional[PriorityLevel] = None

class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime