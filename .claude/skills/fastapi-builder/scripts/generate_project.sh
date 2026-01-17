`#!/bin/bash

# FastAPI Project Generator Script
# Creates a complete FastAPI project structure with customizable options

set -e

# Default values
PROJECT_NAME="my-fastapi-app"
DATABASE_TYPE="none"
AUTH_TYPE="none"
INCLUDE_TESTS=true
INCLUDE_DOCKER=false

# Print usage information
usage() {
    echo "Usage: $0 --name PROJECT_NAME [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --name NAME          Project name (required)"
    echo "  --database TYPE      Database type: none, sqlalchemy, tortoise (default: none)"
    echo "  --auth TYPE          Authentication type: none, jwt, oauth2 (default: none)"
    echo "  --tests              Include tests (default: true)"
    echo "  --no-tests           Exclude tests"
    echo "  --docker             Include Docker configuration"
    echo "  --help               Show this help message"
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --database)
            DATABASE_TYPE="$2"
            shift 2
            ;;
        --auth)
            AUTH_TYPE="$2"
            shift 2
            ;;
        --tests)
            INCLUDE_TESTS=true
            shift
            ;;
        --no-tests)
            INCLUDE_TESTS=false
            shift
            ;;
        --docker)
            INCLUDE_DOCKER=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$PROJECT_NAME" ]]; then
    echo "Error: Project name is required"
    usage
fi

# Validate database type
if [[ ! "$DATABASE_TYPE" =~ ^(none|sqlalchemy|tortoise)$ ]]; then
    echo "Error: Invalid database type. Must be one of: none, sqlalchemy, tortoise"
    exit 1
fi

# Validate auth type
if [[ ! "$AUTH_TYPE" =~ ^(none|jwt|oauth2)$ ]]; then
    echo "Error: Invalid auth type. Must be one of: none, jwt, oauth2"
    exit 1
fi

echo "Creating FastAPI project: $PROJECT_NAME"
echo "Database: $DATABASE_TYPE"
echo "Authentication: $AUTH_TYPE"
echo "Include tests: $INCLUDE_TESTS"
echo "Include Docker: $INCLUDE_DOCKER"
echo ""

# Create project directory
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Create directory structure
mkdir -p app
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/routes
mkdir -p app/utils

if [[ "$INCLUDE_TESTS" == true ]]; then
    mkdir -p tests
fi

# Create main.py
cat > app/main.py << EOF
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import your route modules here
# from app.routes import users, items

app = FastAPI(
    title="${PROJECT_NAME}",
    description="A FastAPI application",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to ${PROJECT_NAME}!"}

# Include your routes here
# app.include_router(users.router, prefix="/users", tags=["users"])
# app.include_router(items.router, prefix="/items", tags=["items"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Create config.py
cat > app/config.py << EOF
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "${PROJECT_NAME}"
    admin_email: str = "admin@example.com"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./${PROJECT_NAME}.db")
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-this")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create database.py based on database type
if [[ "$DATABASE_TYPE" == "sqlalchemy" ]]; then
cat > app/database.py << EOF
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
EOF
elif [[ "$DATABASE_TYPE" == "tortoise" ]]; then
cat > app/database.py << EOF
from tortoise import Tortoise
from app.config import settings

async def init_db():
    await Tortoise.init(
        db_url=settings.database_url,
        modules={"models": ["app.models"]},
    )
    await Tortoise.generate_schemas()

async def close_db():
    await Tortoise.close_connections()
EOF
fi

# Create auth.py if authentication is enabled
if [[ "$AUTH_TYPE" != "none" ]]; then
cat > app/auth.py << EOF
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.config import settings

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Token models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str):
    # This is a placeholder - implement your user lookup logic
    # user = get_user_from_db(username)
    # if not user or not verify_password(password, user.hashed_password):
    #     return False
    # return user
    pass

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[settings.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    # user = get_user(username=token_data.username)
    # if user is None:
    #     raise credentials_exception
    # return user
EOF
fi

# Create requirements.txt
cat > requirements.txt << EOF
fastapi==0.104.1
uvicorn[standard]
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
requests==2.31.0
pytest==7.4.3
httpx==0.25.2
SQLAlchemy==2.0.23
alembic==1.12.1
$(if [[ "$DATABASE_TYPE" == "tortoise" ]]; then echo "tortoise-orm==0.20.0"; fi)
$(if [[ "$AUTH_TYPE" != "none" ]]; then echo "python-jose[cryptography]==3.3.0"; fi)
$(if [[ "$AUTH_TYPE" != "none" ]]; then echo "passlib[bcrypt]==1.7.4"; fi)
python-multipart==0.0.6
aiofiles==23.2.1
cryptography==41.0.8
EOF

# Build dependencies list dynamically
dependencies_list='    "fastapi==0.104.1",
    "uvicorn[standard]",
    "pydantic==2.5.0",
    "pydantic-settings==2.1.0",
    "python-multipart==0.0.6",
    "requests==2.31.0",
    "pytest==7.4.3",
    "httpx==0.25.2",
    "SQLAlchemy==2.0.23",
    "alembic==1.12.1",
    "aiofiles==23.2.1",
    "cryptography==41.0.8"'

# Add database-specific dependencies
if [[ "$DATABASE_TYPE" == "tortoise" ]]; then
    dependencies_list="${dependencies_list}, \"tortoise-orm==0.20.0\""
fi

# Add auth-specific dependencies
if [[ "$AUTH_TYPE" != "none" ]]; then
    dependencies_list="${dependencies_list}, \"python-jose[cryptography]==3.3.0\", \"passlib[bcrypt]==1.7.4\""
fi

# Create pyproject.toml for modern Python project management with uv
cat > pyproject.toml << EOF
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "${PROJECT_NAME}"
version = "1.0.0"
description = "A FastAPI application generated with FastAPI Builder skill"
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
$dependencies_list
]

[project.optional-dependencies]
dev = [
    "pytest",
    "black",
    "flake8",
    "mypy",
    "isort"
]

[tool.setuptools.packages.find]
where = ["."]
include = ["app*"]

[tool.uv]
dev-dependencies = [
    "pytest",
    "black",
    "flake8",
    "mypy",
    "isort"
]
EOF

# Create uv.lock file (will be populated after installing dependencies)
touch uv.lock

# Create .python-version file for pyenv/uv compatibility
echo "3.11" > .python-version

# Create Makefile with uv commands
cat > Makefile << EOF
.PHONY: install run dev test format lint check

# Install dependencies using uv
install:
	uv sync --all-extras

# Install in development mode
dev:
	uv sync --all-extras --dev

# Run the application
run:
	uv run uvicorn app.main:app --reload

# Run tests
test:
	uv run pytest

# Format code
format:
	uv run black .
	uv run isort .

# Lint code
lint:
	uv run flake8 .
	uv run mypy .

# Check dependencies
check:
	uv sync --locked

# Run all checks
check-all: format lint test
EOF

# Create .uv.toml configuration
cat > .uv.toml << EOF
[project]
name = "${PROJECT_NAME}"
version = "1.0.0"
requires-python = ">=3.8"
EOF

# Create .gitignore
cat > .gitignore << EOF
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.idea/
.vscode/
.DS_Store
*.swp
*.swo
*~
/__pycache__/
*.sqlite3
.env
.dockerignore
EOF

# Create README.md
cat > README.md << EOF
# ${PROJECT_NAME}

A FastAPI application generated with FastAPI Builder skill.

## Setup with uv (Recommended)

uv is an extremely fast Python package manager written in Rust. It's the recommended way to manage this project.

1. Install uv (if not already installed):
\`\`\`bash
curl -LsSf https://astral.sh/uv/install.sh | sh
\`\`\`

2. Install dependencies:
\`\`\`bash
uv sync
\`\`\`

3. Run the application:
\`\`\`bash
uv run uvicorn app.main:app --reload
\`\`\`

## Alternative Setup with pip

If you prefer to use pip instead of uv:

1. Create a virtual environment:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Run the application:
\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

## Development Commands

This project includes a Makefile with convenient commands:

- \`make install\`: Install dependencies with uv
- \`make dev\`: Install dependencies in development mode
- \`make run\`: Run the application
- \`make test\`: Run tests
- \`make format\`: Format code with black and isort
- \`make lint\`: Lint code with flake8 and mypy
- \`make check-all\`: Run all checks (format, lint, test)

## Project Structure

- \`app/main.py\`: Application entry point
- \`app/config.py\`: Configuration settings
- \`app/models/\`: Database models
- \`app/schemas/\`: Pydantic schemas
- \`app/routes/\`: API route definitions
- \`app/utils/\`: Utility functions
- \`tests/\`: Test files (if included)
- \`pyproject.toml\`: Project metadata and dependencies
- \`uv.lock\`: Lockfile for reproducible builds
- \`.python-version\`: Specifies Python version for pyenv/uv

## API Documentation

- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
EOF

# Create test files if tests are included
if [[ "$INCLUDE_TESTS" == true ]]; then
cat > tests/conftest.py << EOF
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
EOF

cat > tests/test_main.py << EOF
def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
EOF
fi

# Create Dockerfile if requested
if [[ "$INCLUDE_DOCKER" == true ]]; then
cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker-compose.yml << EOF
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=sqlite:///./app.db
    command: uvicorn app.main:app --host 0.0.0.0 --reload
EOF
fi

echo "FastAPI project '$PROJECT_NAME' has been created successfully!"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_NAME"
if [[ "$DATABASE_TYPE" != "none" ]]; then
    echo "2. Set up your database (if using SQLAlchemy, run: alembic init -c alembic/alembic.ini alembic)"
fi
echo "3. Install dependencies: pip install -r requirements.txt"
echo "4. Run the application: uvicorn app.main:app --reload"
echo ""
echo "The application will be available at http://localhost:8000"
echo "API documentation at http://localhost:8000/docs"
