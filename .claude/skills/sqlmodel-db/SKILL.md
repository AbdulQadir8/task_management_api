---
name: sqlmodel-db
description: "Comprehensive SQLModel database design and management for FastAPI applications. Use when Claude needs to work with SQLModel for: (1) Creating database models, (2) Setting up database connections, (3) Implementing CRUD operations, (4) Managing relationships between tables, (5) Designing database schemas for FastAPI projects, or (6) Handling database migrations and sessions."
---

# SQLModel Database Management for FastAPI

## Overview

This skill provides comprehensive tools and guidance for designing and managing databases using SQLModel in FastAPI applications. SQLModel combines the power of SQLAlchemy and Pydantic, offering a simplified interface for database operations while maintaining compatibility with FastAPI's type system.

## Quick Start

When working with SQLModel in FastAPI applications, follow these basic steps:

1. Define your database models using SQLModel
2. Set up database connection and session management
3. Implement CRUD operations using the models
4. Integrate with FastAPI endpoints

### Basic Model Definition
```python
from sqlmodel import Field, SQLModel
from typing import Optional

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None
```

## Core Capabilities

### 1. Database Model Creation
- Define models with proper field types and constraints
- Handle relationships between models (one-to-many, many-to-many)
- Set up proper indexing and unique constraints
- Manage UUID identifiers and automatic ID generation

### 2. Database Connection & Session Management
- Configure database engines (SQLite, PostgreSQL, MySQL)
- Implement session dependency injection for FastAPI
- Handle connection pooling and optimization
- Set up database URL configuration

### 3. CRUD Operations Implementation
- Create standard create, read, update, delete endpoints
- Handle complex queries with filtering and pagination
- Implement proper error handling and validation
- Support for bulk operations

### 4. Relationship Handling
- Define and manage foreign key relationships
- Handle JOIN operations and related data retrieval
- Manage many-to-many relationships with link tables
- Implement cascade delete operations

## Database Model Design

### Basic Model Structure
```python
from sqlmodel import Field, SQLModel, create_engine
from typing import Optional
import uuid
from datetime import datetime

class BaseModel(SQLModel):
    """Base model with common fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class User(BaseModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, min_length=3, max_length=50)
    email: str = Field(unique=True, min_length=5, max_length=100)
    is_active: bool = Field(default=True)
```

### Relationship Examples
```python
from sqlmodel import Relationship, Field
from typing import List, Optional

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=50)
    headquarters: str

    heroes: List["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(min_length=1, max_length=50)
    secret_name: str
    age: Optional[int] = None

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional[Team] = Relationship(back_populates="heroes")
```

## FastAPI Integration

### Database Session Dependency
```python
from sqlmodel import Session, create_engine
from fastapi import Depends

# Create engine (configure URL as needed)
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)

def get_session():
    with Session(engine) as session:
        yield session
```

### Example CRUD Endpoint
```python
from fastapi import FastAPI, HTTPException
from typing import List
from sqlmodel import select

app = FastAPI()

@app.post("/heroes/", response_model=Hero)
def create_hero(hero: Hero, session: Session = Depends(get_session)):
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero

@app.get("/heroes/", response_model=List[Hero])
def read_heroes(
    session: Session = Depends(get_session),
    offset: int = 0,
    limit: int = 100
):
    heroes = session.exec(select(Hero).offset(offset).limit(limit)).all()
    return heroes
```

## Best Practices

### Model Validation
- Use Pydantic validation parameters (min_length, max_length, regex)
- Implement custom validators when needed
- Use proper typing for better IDE support

### Error Handling
- Handle database connection errors gracefully
- Implement proper 404 responses for missing resources
- Use transaction management for complex operations

### Performance
- Use proper indexing for frequently queried fields
- Implement pagination for large datasets
- Use select statements efficiently to avoid N+1 queries

## Resources

This skill provides the following resources for SQLModel database management:

### scripts/
- Database setup and initialization scripts
- Model generation utilities
- Migration helpers
- Sample CRUD operation implementations

### references/
- SQLModel API reference documentation
- Database design patterns for FastAPI
- Performance optimization guidelines
- Security best practices

### assets/
- FastAPI project templates with SQLModel
- Common model patterns and boilerplate
- Configuration files for different databases
