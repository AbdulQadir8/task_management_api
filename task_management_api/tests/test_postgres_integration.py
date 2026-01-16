"""
Integration tests for Neon PostgreSQL database
"""
import pytest
from sqlmodel import Session, select
from app.models.task import Task, TaskCreate, PriorityLevel


def test_postgres_integration(postgres_session):
    """Test basic functionality with PostgreSQL database"""
    # Test creating a task
    task_data = TaskCreate(
        title="Integration Test Task",
        description="Task created in PostgreSQL integration test",
        is_completed=False,
        priority=PriorityLevel.HIGH
    )

    # Create the task in the database
    new_task = Task.model_validate(task_data)
    postgres_session.add(new_task)
    postgres_session.commit()
    postgres_session.refresh(new_task)

    # Verify the task was created
    assert new_task.id is not None
    assert new_task.title == "Integration Test Task"
    assert new_task.priority == PriorityLevel.HIGH
    assert new_task.is_completed is False

    # Test reading the task back
    task_id = new_task.id
    retrieved_task = postgres_session.get(Task, task_id)
    assert retrieved_task is not None
    assert retrieved_task.title == "Integration Test Task"

    # Test updating the task
    retrieved_task.is_completed = True
    postgres_session.add(retrieved_task)
    postgres_session.commit()
    postgres_session.refresh(retrieved_task)

    assert retrieved_task.is_completed is True

    # Test deleting the task
    postgres_session.delete(retrieved_task)
    postgres_session.commit()

    # Verify deletion
    deleted_task = postgres_session.get(Task, task_id)
    assert deleted_task is None


def test_postgres_priority_enum(postgres_session):
    """Test that PostgreSQL enum works correctly"""
    # Create tasks with different priority levels
    created_tasks = []
    for priority in PriorityLevel:
        task_data = Task(
            title=f"Task with {priority} priority",
            description=f"Task with {priority} priority level",
            is_completed=False,
            priority=priority
        )
        postgres_session.add(task_data)
        postgres_session.commit()
        postgres_session.refresh(task_data)

        assert task_data.priority == priority
        created_tasks.append(task_data.id)

    # Verify all tasks were created with correct priority
    for priority in PriorityLevel:
        statement = select(Task).where(Task.title == f"Task with {priority} priority")
        result = postgres_session.exec(statement).first()
        assert result is not None
        assert result.priority == priority

    # Clean up
    for task_id in created_tasks:
        task_to_delete = postgres_session.get(Task, task_id)
        if task_to_delete:
            postgres_session.delete(task_to_delete)
    postgres_session.commit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])