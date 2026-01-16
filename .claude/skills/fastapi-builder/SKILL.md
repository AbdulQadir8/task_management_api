---
name: fastapi-builder
description: Comprehensive FastAPI application generator with project structure, standard endpoints, database integration, authentication, and testing frameworks. Use when creating new FastAPI projects, scaffolding API endpoints, setting up database connections, implementing authentication systems, or generating test suites for FastAPI applications.
---

# FastAPI Builder

## Overview

The FastAPI Builder skill provides comprehensive tools for creating and managing FastAPI applications with best practices. It includes project scaffolding with modern Python tooling (uv package manager), endpoint generation, database integration, authentication setup, and testing frameworks to accelerate FastAPI development.

## Core Capabilities

### 1. Project Scaffolding
Generate a complete FastAPI project structure with:
- Proper directory organization
- Configuration files
- Modern Python project management with pyproject.toml
- uv package manager integration for fast dependency management
- Docker configuration
- Testing setup
- Pre-configured Makefile with development commands

### 2. Endpoint Generation
Automatically create CRUD endpoints for resources with:
- Request/response schema definitions
- Database models
- Route handlers with proper error handling
- Validation and serialization

### 3. Database Integration
Set up database connections and models with:
- SQLAlchemy or Tortoise ORM support
- Connection pooling
- Migration configuration
- Session management

### 4. Authentication Systems
Implement security features including:
- JWT token authentication
- Password hashing
- User management
- Role-based access control

### 5. Modern Python Tooling
Includes support for:
- uv: Extremely fast Python package manager written in Rust
- pyproject.toml: Modern Python project configuration
- uv.lock: Reproducible dependency locking
- Makefile: Convenient development commands
- .python-version: Python version specification

## Quick Start

### Creating a Basic API Server
```python
from fastapi import FastAPI

app = FastAPI(title="My API", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### Project Generation
Use the project generator script to create a well-structured FastAPI application with uv integration:

```bash
bash scripts/generate_project.sh --name myapp --database sqlalchemy --auth jwt
```

This creates a project with:
- app/
  - main.py (application entry point)
  - config.py (configuration settings)
  - models/ (database models)
  - schemas/ (Pydantic schemas)
  - routes/ (API endpoints)
  - database.py (database connection)
  - auth.py (authentication utilities)
  - dependencies.py (dependency injection)
- tests/
  - conftest.py (test configuration)
  - test_*.py (individual test files)
- requirements.txt (traditional pip dependencies)
- pyproject.toml (modern Python project configuration)
- uv.lock (reproducible dependency lockfile)
- .python-version (Python version specification)
- Makefile (convenient development commands)
- Dockerfile
- docker-compose.yml

### Project Setup with uv (Recommended)

After generating the project, navigate to the project directory and use uv for fast dependency management:

```bash
cd myapp
uv sync          # Install dependencies with uv
uv run uvicorn app.main:app --reload    # Run the application
```

Or use the convenient Makefile commands:
```bash
make install     # Install dependencies with uv
make run         # Run the application
make test        # Run tests
make format      # Format code
```

### Adding a CRUD Resource
```python
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)
```

## Common Patterns

### Dependency Injection
```python
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_settings():
    return settings
```

### Error Handling
```python
from fastapi import HTTPException, status

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item ID must be positive"
        )
    # ... rest of the function
```

### Request Validation
```python
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = Field(default=None, max_length=500)
```

## Scripts

The skill includes several helper scripts:

### Project Generation Script
- `scripts/generate_project.sh`: Creates a complete FastAPI project with customizable options

### Endpoint Generator
- `scripts/generate_endpoint.py`: Generates CRUD endpoints for specified resources

### Setup Scripts
- `scripts/setup_auth.py`: Sets up authentication system
- `scripts/setup_database.py`: Configures database connection

## Resources

This skill leverages FastAPI's powerful features and modern Python tooling to accelerate development:

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Pydantic Documentation: https://pydantic-docs.helpmanual.io/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Starlette Documentation: https://www.starlette.io/
- uv Documentation: https://docs.astral.sh/uv/
- Python Project Guidelines: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
