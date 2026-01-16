# SQLModel with FastAPI Best Practices

This document outlines best practices for integrating SQLModel with FastAPI applications.

## Project Structure

Recommended project structure for SQLModel + FastAPI applications:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── routers/
│   │       │   ├── __init__.py
│   │       │   ├── users.py
│   │       │   └── items.py
│   │       └── deps.py      # Dependencies including DB session
│   ├── models/              # SQLModel database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   ├── schemas/             # Pydantic models for API requests/responses
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── item.py
│   └── db/
│       ├── __init__.py
│       ├── base.py          # Base model and engine setup
│       └── session.py       # Session dependency
```

## Model Separation Pattern

Always separate database models from API models:

```python
# models/user.py (Database models)
from sqlmodel import Field, SQLModel
from typing import Optional

class UserBase(SQLModel):
    email: str
    is_active: bool = True

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

class UserCreate(UserBase):
    password: str

# schemas/user.py (API models)
from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        orm_mode = True
```

## Database Session Management

### Session Dependency

```python
# app/db/session.py
from sqlmodel import Session
from app.db.base import engine

def get_session():
    with Session(engine) as session:
        yield session
```

### Using in Routers

```python
# app/api/v1/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.models.user import User
from app.schemas.user import User as UserSchema, UserCreate
from app.db.session import get_session

router = APIRouter()

@router.post("/", response_model=UserSchema)
def create_user(
    user: UserCreate,
    session: Session = Depends(get_session)
):
    db_user = User.from_orm(user)  # Convert from API model to DB model
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user  # Will be converted to API model automatically
```

## Error Handling

### Custom Exceptions

```python
# app/core/exceptions.py
from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

class DuplicateEmailException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {email} already exists"
        )
```

### Exception Handlers

```python
# app/main.py
from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError
from app.core.exceptions import UserNotFoundException, DuplicateEmailException

app = FastAPI()

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    if "duplicate key value violates unique constraint" in str(exc.orig):
        return JSONResponse(
            status_code=409,
            content={"detail": "Duplicate entry detected"}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )
```

## Security Considerations

### Password Hashing

```python
# app/utils/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)
```

### Protecting Sensitive Fields

```python
# models/user.py
from sqlmodel import Field, SQLModel
from pydantic import Field as PydanticField
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str = Field(exclude=True)  # Exclude from responses
    is_active: bool = True
```

## Performance Optimization

### Proper Indexing

```python
# models/item.py
from sqlmodel import Field, SQLModel
from typing import Optional

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)  # Index for frequent searches
    owner_id: int = Field(index=True, foreign_key="user.id")  # Index foreign keys used in joins
    category: str = Field(index=True)  # Index for filtering
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
```

### Pagination

```python
# api/v1/routers/items.py
from typing import List
from fastapi import Query

@router.get("/", response_model=List[Item])
def read_items(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=100)
):
    items = session.exec(
        select(Item).offset(skip).limit(limit)
    ).all()
    return items
```

### Avoiding N+1 Queries

```python
# Bad: causes N+1 query problem
@router.get("/{user_id}/items", response_model=List[Item])
def read_user_items_bad(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    return user.items  # This executes a separate query for each item

# Good: uses explicit join to avoid N+1
@router.get("/{user_id}/items", response_model=List[Item])
def read_user_items_good(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    # Pre-load the items to avoid N+1
    return session.exec(
        select(Item).where(Item.owner_id == user_id)
    ).all()
```

## Testing Considerations

### Test Database Setup

```python
# tests/conftest.py
import pytest
from sqlmodel import create_engine
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import SQLModel

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
```

### Async Session Handling

```python
# For async tests
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_test_session():
    # Implementation for async session handling
    pass
```

## Deployment Considerations

### Connection Pooling

```python
# app/db/base.py
from sqlmodel import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
)
```

### Environment Variables

```python
# app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///./test.db"
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
```