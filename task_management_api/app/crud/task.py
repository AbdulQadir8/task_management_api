from sqlmodel import Session, select
from app.models.task import Task, TaskCreate, TaskUpdate, PriorityLevel
from datetime import datetime
from typing import Optional, List

def create_task(session: Session, task: TaskCreate) -> Task:
    """Create a new task"""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def get_task(session: Session, task_id: int) -> Optional[Task]:
    """Get a task by ID"""
    statement = select(Task).where(Task.id == task_id)
    return session.exec(statement).first()

def get_tasks(
    session: Session,
    skip: int = 0,
    limit: int = 100,
    is_completed: Optional[bool] = None,
    priority: Optional[PriorityLevel] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc"
) -> List[Task]:
    """Get all tasks with pagination, filtering, and sorting"""
    statement = select(Task)

    # Apply filters
    if is_completed is not None:
        statement = statement.where(Task.is_completed == is_completed)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    # Apply sorting
    if sort_by == "priority":
        if sort_order == "asc":
            statement = statement.order_by(Task.priority)
        else:
            statement = statement.order_by(Task.priority.desc())
    elif sort_by == "title":
        if sort_order == "asc":
            statement = statement.order_by(Task.title)
        else:
            statement = statement.order_by(Task.title.desc())
    elif sort_by == "created_at":
        if sort_order == "asc":
            statement = statement.order_by(Task.created_at)
        else:
            statement = statement.order_by(Task.created_at.desc())
    elif sort_by == "updated_at":
        if sort_order == "asc":
            statement = statement.order_by(Task.updated_at)
        else:
            statement = statement.order_by(Task.updated_at.desc())
    elif sort_by == "is_completed":
        if sort_order == "asc":
            statement = statement.order_by(Task.is_completed)
        else:
            statement = statement.order_by(Task.is_completed.desc())

    # Apply pagination
    statement = statement.offset(skip).limit(limit)
    return session.exec(statement).all()

def update_task(session: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    """Update a task by ID"""
    db_task = get_task(session, task_id)
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)

    from datetime import datetime, timezone
    db_task.updated_at = datetime.now(timezone.utc)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def delete_task(session: Session, task_id: int) -> bool:
    """Delete a task by ID"""
    db_task = get_task(session, task_id)
    if not db_task:
        return False

    session.delete(db_task)
    session.commit()
    return True