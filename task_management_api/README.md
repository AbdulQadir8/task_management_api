# Task Management API

This is a complete Task Management API with full CRUD operations built using FastAPI and SQLModel.

## Features

- Full CRUD operations for tasks
- RESTful API design
- Input validation with Pydantic
- SQLModel for database modeling
- Comprehensive test suite
- Modern Python tooling with uv

## Installation and Setup

This project uses `uv` for fast package management. Make sure you have `uv` installed:

```bash
# Install uv if you don't have it
pip install uv
```

Then set up the project:

```bash
# Clone or navigate to the project directory
cd task_management_api

# Install dependencies with uv
uv sync

# Activate the virtual environment (optional but recommended)
source .venv/bin/activate
```

## Neon PostgreSQL Configuration

The application is configured to use Neon PostgreSQL database by default. To configure your own Neon database:

1. Create a Neon account at [neon.tech](https://neon.tech)
2. Create a new project and copy your connection details
3. Set environment variables (recommended) or update the config:

```bash
export POSTGRES_USER="your_username"
export POSTGRES_PASSWORD="your_password"
export POSTGRES_HOST="your_project.region.aws.neon.tech"
export POSTGRES_DB="your_database"
```

By default, the application will fall back to SQLite for local development if `USE_SQLITE_FALLBACK=true` is set in the environment.

## Running the Application

```bash
# Run the application
uv run uvicorn app.main:app --reload

# The API will be available at http://localhost:8000
# Interactive documentation at http://localhost:8000/docs
```

## API Endpoints

### Base URL
`http://localhost:8000/api/v1`

### 1. Create a Task
- **Method**: POST
- **Endpoint**: `/tasks/`
- **Description**: Create a new task
- **Request Body**:
```json
{
  "title": "string (required, 1-100 characters)",
  "description": "string (optional, max 500 characters)",
  "is_completed": "boolean (default: false)",
  "priority": "string (default: medium, options: low, medium, high, urgent)"
}
```
- **Response**: 201 Created
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "is_completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the task management API",
    "is_completed": false
  }'
```

### 2. Get a Task
- **Method**: GET
- **Endpoint**: `/tasks/{task_id}`
- **Description**: Get a specific task by ID
- **Path Parameter**: `task_id` (integer)
- **Response**: 200 OK
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "is_completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Example**:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1"
```

### 3. List All Tasks
- **Method**: GET
- **Endpoint**: `/tasks/`
- **Description**: Get all tasks with pagination, filtering, and sorting
- **Query Parameters**:
  - `skip` (integer, default: 0)
  - `limit` (integer, default: 100)
  - `is_completed` (boolean, optional, filter by completion status)
  - `priority` (string, optional, filter by priority level: low, medium, high, urgent)
  - `sort_by` (string, default: created_at, options: title, created_at, updated_at, is_completed, priority)
  - `sort_order` (string, default: desc, options: asc, desc)
- **Response**: 200 OK
```json
[
  {
    "id": "integer",
    "title": "string",
    "description": "string",
    "is_completed": "boolean",
    "priority": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```
- **Examples**:
```bash
# Get all tasks
curl -X GET "http://localhost:8000/api/v1/tasks/"

# Get only completed tasks
curl -X GET "http://localhost:8000/api/v1/tasks/?is_completed=true"

# Get only high priority tasks
curl -X GET "http://localhost:8000/api/v1/tasks/?priority=high"

# Get tasks sorted by priority (descending)
curl -X GET "http://localhost:8000/api/v1/tasks/?sort_by=priority&sort_order=desc"

# Get tasks sorted by title (ascending)
curl -X GET "http://localhost:8000/api/v1/tasks/?sort_by=title&sort_order=asc"

# Combined filtering and sorting
curl -X GET "http://localhost:8000/api/v1/tasks/?is_completed=false&priority=high&sort_by=created_at&sort_order=asc"
```

### 4. Update a Task
- **Method**: PUT
- **Endpoint**: `/tasks/{task_id}`
- **Description**: Update an existing task
- **Path Parameter**: `task_id` (integer)
- **Request Body**:
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "is_completed": "boolean (optional)",
  "priority": "string (optional, options: low, medium, high, urgent)"
}
```
- **Response**: 200 OK
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "is_completed": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Example**:
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "is_completed": true
  }'
```

### 5. Delete a Task
- **Method**: DELETE
- **Endpoint**: `/tasks/{task_id}`
- **Description**: Delete a task by ID
- **Path Parameter**: `task_id` (integer)
- **Response**: 200 OK
```json
{
  "message": "Task deleted successfully"
}
```
- **Example**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

## Error Responses

All endpoints return appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Successfully created resource
- `404 Not Found`: Resource does not exist
- `422 Unprocessable Entity`: Invalid request parameters

## Testing

Run the tests with pytest:

```bash
# Run all tests
uv run pytest tests/

# Run tests with verbose output
uv run pytest tests/ -v

# Run tests and show coverage
uv run pytest tests/ --cov=app
```

All tests should pass, ensuring the API functions correctly.

## Project Structure

```
task_management_api/
├── app/
│   ├── main.py             # Main application entry point
│   ├── database.py         # Database configuration
│   ├── models/
│   │   └── task.py        # Task model definitions
│   ├── schemas/            # Pydantic schemas (now integrated in models)
│   ├── crud/
│   │   └── task.py        # CRUD operations
│   └── routes/
│       └── tasks.py       # API route handlers
├── tests/
│   ├── conftest.py        # Test configuration
│   ├── test_tasks.py      # Task API tests
│   └── test_main.py       # Main app tests
├── pyproject.toml         # Project dependencies and metadata
├── uv.lock               # Dependency lock file
├── Makefile              # Convenient commands
└── README.md             # Project documentation
```

## Commands

The project includes a Makefile with convenient commands:

```bash
# Install dependencies
make install

# Run the application
make run

# Run tests
make test

# Run tests with coverage
make test-cov

# Clean Python cache files
make clean

# Format code with black
make format

# Lint code with flake8
make lint
```