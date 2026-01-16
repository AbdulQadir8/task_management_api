from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session
from typing import List, Optional
from app.database import get_session
from app.models.task import Task, TaskCreate, TaskUpdate, TaskResponse, PriorityLevel
from app.crud.task import (
    create_task,
    get_task,
    get_tasks,
    update_task,
    delete_task
)

router = APIRouter()

@router.post("/tasks/", response_model=TaskResponse, status_code=201)
def create_new_task(task: TaskCreate, session: Session = Depends(get_session)):
    """Create a new task"""
    db_task = create_task(session, task)
    return db_task

@router.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int, session: Session = Depends(get_session)):
    """Get a specific task by ID"""
    db_task = get_task(session, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.get("/tasks/", response_model=List[TaskResponse])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
    priority: Optional[PriorityLevel] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    session: Session = Depends(get_session)
):
    """Get all tasks with pagination, filtering, and sorting"""
    tasks = get_tasks(
        session,
        skip=skip,
        limit=limit,
        is_completed=is_completed,
        priority=priority,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return tasks

@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_existing_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing task"""
    db_task = update_task(session, task_id, task_update)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.delete("/tasks/{task_id}")
def delete_existing_task(task_id: int, session: Session = Depends(get_session)):
    """Delete a task"""
    success = delete_task(session, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}