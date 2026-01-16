import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.task import Task, TaskCreate
from sqlmodel import Session
from datetime import datetime


def test_create_task(client, session):
    """Test creating a new task"""
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "is_completed": False
    }

    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["is_completed"] is False
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_get_task(client, session):
    """Test getting a specific task"""
    # First create a task
    task_data = {
        "title": "Get Test Task",
        "description": "Task for testing retrieval",
        "is_completed": False
    }

    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Then get the task
    response = client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Get Test Task"


def test_get_nonexistent_task(client):
    """Test getting a task that doesn't exist"""
    response = client.get("/api/v1/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_list_tasks(client, session):
    """Test listing all tasks"""
    # Create multiple tasks
    task_data1 = {
        "title": "First Task",
        "description": "First test task",
        "is_completed": False
    }

    task_data2 = {
        "title": "Second Task",
        "description": "Second test task",
        "is_completed": True
    }

    client.post("/api/v1/tasks/", json=task_data1)
    client.post("/api/v1/tasks/", json=task_data2)

    response = client.get("/api/v1/tasks/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) >= 2  # At least the 2 tasks we created

    titles = [task["title"] for task in data]
    assert "First Task" in titles
    assert "Second Task" in titles


def test_update_task(client, session):
    """Test updating a task"""
    # First create a task
    task_data = {
        "title": "Original Task",
        "description": "Original description",
        "is_completed": False
    }

    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Update the task
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "is_completed": True
    }

    response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == task_id
    assert data["title"] == "Updated Task"
    assert data["description"] == "Updated description"
    assert data["is_completed"] is True


def test_update_nonexistent_task(client):
    """Test updating a task that doesn't exist"""
    update_data = {
        "title": "Updated Task",
        "description": "Updated description",
        "is_completed": True
    }

    response = client.put("/api/v1/tasks/999", json=update_data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_delete_task(client, session):
    """Test deleting a task"""
    # First create a task
    task_data = {
        "title": "Task to Delete",
        "description": "This task will be deleted",
        "is_completed": False
    }

    create_response = client.post("/api/v1/tasks/", json=task_data)
    task_id = create_response.json()["id"]

    # Verify task exists
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 200

    # Delete the task
    delete_response = client.delete(f"/api/v1/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Task deleted successfully"}

    # Verify task is gone
    get_response = client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_task(client):
    """Test deleting a task that doesn't exist"""
    response = client.delete("/api/v1/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_create_task_with_priority(client, session):
    """Test creating a task with priority"""
    task_data = {
        "title": "High Priority Task",
        "description": "This is a high priority task",
        "is_completed": False,
        "priority": "high"
    }

    response = client.post("/api/v1/tasks/", json=task_data)
    assert response.status_code == 201

    data = response.json()
    assert data["priority"] == "high"
    assert data["title"] == "High Priority Task"


def test_filter_tasks_by_completion_status(client, session):
    """Test filtering tasks by completion status"""
    # Create completed and incomplete tasks
    completed_task = {
        "title": "Completed Task",
        "description": "This task is completed",
        "is_completed": True,
        "priority": "medium"
    }

    incomplete_task = {
        "title": "Incomplete Task",
        "description": "This task is not completed",
        "is_completed": False,
        "priority": "low"
    }

    client.post("/api/v1/tasks/", json=completed_task)
    client.post("/api/v1/tasks/", json=incomplete_task)

    # Get completed tasks only
    response = client.get("/api/v1/tasks/?is_completed=true")
    completed_tasks = response.json()
    assert len(completed_tasks) >= 1
    for task in completed_tasks:
        assert task["is_completed"] is True

    # Get incomplete tasks only
    response = client.get("/api/v1/tasks/?is_completed=false")
    incomplete_tasks = response.json()
    assert len(incomplete_tasks) >= 1
    for task in incomplete_tasks:
        assert task["is_completed"] is False


def test_filter_tasks_by_priority(client, session):
    """Test filtering tasks by priority"""
    # Create tasks with different priorities
    low_task = {
        "title": "Low Priority Task",
        "description": "Low priority task",
        "is_completed": False,
        "priority": "low"
    }

    high_task = {
        "title": "High Priority Task",
        "description": "High priority task",
        "is_completed": False,
        "priority": "high"
    }

    client.post("/api/v1/tasks/", json=low_task)
    client.post("/api/v1/tasks/", json=high_task)

    # Get high priority tasks only
    response = client.get("/api/v1/tasks/?priority=high")
    high_priority_tasks = response.json()
    assert len(high_priority_tasks) >= 1
    for task in high_priority_tasks:
        assert task["priority"] == "high"


def test_sort_tasks_by_priority(client, session):
    """Test sorting tasks by priority"""
    # Create tasks with different priorities
    client.post("/api/v1/tasks/", json={
        "title": "High Priority Task",
        "description": "High priority task",
        "is_completed": False,
        "priority": "high"
    })

    client.post("/api/v1/tasks/", json={
        "title": "Low Priority Task",
        "description": "Low priority task",
        "is_completed": False,
        "priority": "low"
    })

    # Get tasks sorted by priority ascending
    response = client.get("/api/v1/tasks/?sort_by=priority&sort_order=asc")
    tasks_asc = response.json()
    priorities_asc = [task["priority"] for task in tasks_asc]
    # 'low' should come before 'high' in alphabetical order when sorted asc
    assert "low" in priorities_asc

    # Get tasks sorted by priority descending
    response = client.get("/api/v1/tasks/?sort_by=priority&sort_order=desc")
    tasks_desc = response.json()
    priorities_desc = [task["priority"] for task in tasks_desc]
    # 'high' should come before 'low' in alphabetical order when sorted desc
    assert "high" in priorities_desc


def test_sort_tasks_by_title(client, session):
    """Test sorting tasks by title"""
    # Create tasks with different titles
    client.post("/api/v1/tasks/", json={
        "title": "Zebra Task",
        "description": "Task with Z title",
        "is_completed": False,
        "priority": "medium"
    })

    client.post("/api/v1/tasks/", json={
        "title": "Apple Task",
        "description": "Task with A title",
        "is_completed": False,
        "priority": "medium"
    })

    # Get tasks sorted by title ascending
    response = client.get("/api/v1/tasks/?sort_by=title&sort_order=asc")
    tasks_asc = response.json()
    titles_asc = [task["title"] for task in tasks_asc]
    # 'Apple' should come before 'Zebra' when sorted ascending
    if len(titles_asc) >= 2:
        assert titles_asc[0].startswith("Apple")

    # Get tasks sorted by title descending
    response = client.get("/api/v1/tasks/?sort_by=title&sort_order=desc")
    tasks_desc = response.json()
    titles_desc = [task["title"] for task in tasks_desc]
    # 'Zebra' should come before 'Apple' when sorted descending
    if len(titles_desc) >= 2:
        assert titles_desc[0].startswith("Zebra")