---
name: test-driven-development
description: Comprehensive Test-Driven Development (TDD) workflow guidance with pytest, including red-green-refactor cycle, test-first methodology, and best practices for Python applications. Use when Claude needs to implement TDD principles, write tests before code, or follow proper testing methodologies in Python projects.
---

# Test-Driven Development (TDD) with Pytest

## Overview

This skill enables Claude to implement proper Test-Driven Development practices using pytest. It provides guidance on the red-green-refactor cycle, writing tests before implementation, and following TDD principles to create high-quality, well-tested Python applications.

## TDD Workflow

### 1. Red Phase - Write a Failing Test
First, write a test that defines the functionality you want to implement. The test should fail initially since the functionality doesn't exist yet.

```python
# Example: Write a test for a function that doesn't exist yet
def test_add_numbers():
    result = add_numbers(2, 3)
    assert result == 5
```

### 2. Green Phase - Make the Test Pass
Implement the minimal code necessary to make the failing test pass. Focus only on making the test pass, not on perfect implementation.

```python
# Minimal implementation to make test pass
def add_numbers(a, b):
    return a + b
```

### 3. Refactor Phase - Improve the Code
Clean up the code, improve readability, and optimize while ensuring all tests continue to pass.

```python
# Refactored implementation with better error handling
def add_numbers(a, b):
    """
    Add two numbers together.

    Args:
        a (int/float): First number
        b (int/float): Second number

    Returns:
        int/float: Sum of a and b
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Arguments must be numbers")
    return a + b
```

## Pytest Best Practices for TDD

### Naming Conventions
- Name test files with the prefix `test_` (e.g., `test_calculator.py`)
- Name test functions with the prefix `test_` (e.g., `test_add_numbers`)
- Use descriptive names that explain what is being tested

### Test Structure (AAA Pattern)
- **Arrange**: Set up test data and conditions
- **Act**: Execute the function or method being tested
- **Assert**: Verify the expected outcome

```python
def test_user_authentication_valid_credentials():
    # Arrange
    user_service = UserService()
    valid_email = "test@example.com"
    valid_password = "password123"

    # Act
    result = user_service.authenticate(valid_email, valid_password)

    # Assert
    assert result is True
    assert user_service.current_user.email == valid_email
```

### Using Fixtures for Test Setup
```python
import pytest

@pytest.fixture
def sample_user():
    return {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com"
    }

def test_create_user(sample_user):
    user_repo = UserRepository()
    result = user_repo.create(sample_user)
    assert result.id == sample_user["id"]
```

## TDD with FastAPI Applications

### Testing Endpoints Before Implementation
```python
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user_endpoint():
    # Test for endpoint that doesn't exist yet
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User"
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]
```

### Implementing Endpoint to Pass Test
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    full_name: str = None

@app.post("/users/", status_code=201)
def create_user(user: User):
    # Simple in-memory storage for example
    user_dict = user.dict()
    user_dict["id"] = 1  # Simplified ID assignment
    return user_dict
```

## Common TDD Scenarios

### Unit Testing Functions
```python
# Write test first
def test_calculate_discount_regular_customer():
    discount = calculate_discount(100, "regular")
    assert discount == 5  # 5% discount for regular customer

# Then implement function
def calculate_discount(amount, customer_type):
    if customer_type == "regular":
        return amount * 0.05
    elif customer_type == "premium":
        return amount * 0.1
    else:
        return 0
```

### Testing Database Operations
```python
def test_user_creation_saves_to_database(test_db_session):
    # Arrange
    user_data = {"name": "Jane Doe", "email": "jane@example.com"}

    # Act
    user = create_user(user_data, test_db_session)

    # Assert
    assert user.id is not None
    assert user.name == user_data["name"]
    assert test_db_session.query(User).filter_by(id=user.id).first() is not None
```

## Running Tests

### Basic Test Execution
```bash
# Run all tests
pytest

# Run tests in specific file
pytest test_example.py

# Run specific test function
pytest test_example.py::test_function_name

# Run tests with verbose output
pytest -v

# Run tests and show print statements
pytest -s
```

### Useful Pytest Options for TDD
```bash
# Stop after first failure
pytest -x

# Run only failed tests from last run
pytest --lf

# Run tests that match a keyword pattern
pytest -k "test_user"

# Show coverage report
pytest --cov=src
```
