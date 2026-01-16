# SQLModel API Reference

This document provides a comprehensive reference for SQLModel classes, methods, and usage patterns.

## Core Classes

### SQLModel
The base class that combines SQLAlchemy and Pydantic functionality.

```python
from sqlmodel import SQLModel

class MyModel(SQLModel, table=True):
    id: int
```

**Parameters:**
- `table`: When True, indicates this model represents a database table

### Field
Used to define column properties in SQLModel models.

```python
from sqlmodel import Field

class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, nullable=False)
```

**Common Parameters:**
- `primary_key=True`: Makes the field a primary key
- `nullable=True/False`: Determines if NULL values are allowed
- `unique=True`: Enforces uniqueness constraint
- `index=True`: Creates a database index for faster queries
- `default=value`: Sets a default value
- `default_factory=function`: Sets a function to generate default values
- `foreign_key="table.column"`: Creates a foreign key relationship

### Relationship
Used to define relationships between models.

```python
from sqlmodel import Relationship

class Team(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str

    heroes: List["Hero"] = Relationship(back_populates="team")

class Hero(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    team_id: int = Field(foreign_key="team.id")

    team: Optional[Team] = Relationship(back_populates="heroes")
```

## Core Functions

### create_engine
Creates a database engine for connecting to the database.

```python
from sqlmodel import create_engine

engine = create_engine("sqlite:///database.db")
```

### select
Used to construct SELECT queries.

```python
from sqlmodel import select

statement = select(User).where(User.name == "John")
results = session.exec(statement).all()
```

### Session
Context manager for database transactions.

```python
from sqlmodel import Session

with Session(engine) as session:
    user = User(name="John", email="john@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)
```

## Common Query Patterns

### Simple Queries
```python
# Get all records
users = session.exec(select(User)).all()

# Get first record
user = session.exec(select(User).where(User.id == 1)).first()

# Limit and offset
users = session.exec(select(User).offset(10).limit(5)).all()
```

### Filtering
```python
# Multiple conditions
users = session.exec(
    select(User)
    .where(User.age > 18)
    .where(User.is_active == True)
).all()

# IN clause
user_ids = [1, 2, 3]
users = session.exec(select(User).where(User.id.in_(user_ids))).all()
```

### Joins
```python
# Join with relationships
results = session.exec(
    select(User, Team)
    .join(Team, User.team_id == Team.id)
).all()
```

## Migration Patterns

### Creating Tables
```python
from sqlmodel import SQLModel

# Create all tables defined in your models
SQLModel.metadata.create_all(engine)
```

### Adding Columns
```python
# For schema changes, consider using Alembic
# SQLModel works with Alembic for proper migrations
```

## FastAPI Integration

### Dependency Injection
```python
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session

@app.get("/users/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user
```

## Best Practices

### Model Design
1. Separate database models from API models when needed
2. Use Pydantic's field validators for input validation
3. Implement proper indexing for frequently queried fields
4. Use UUIDs for sensitive identifiers instead of auto-incrementing integers

### Session Management
1. Use dependency injection for session management in FastAPI
2. Always close sessions properly (use context managers)
3. Handle transaction rollbacks appropriately

### Error Handling
1. Catch database-specific exceptions
2. Implement proper validation error responses
3. Use transactions for multi-step operations