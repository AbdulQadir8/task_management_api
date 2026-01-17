# Task Management API

This is a complete Task Management API with full CRUD operations built using FastAPI and SQLModel. The application provides a robust, scalable solution for managing tasks with modern Python tooling.

## 🚀 Features

- **Full CRUD operations** for tasks with comprehensive API endpoints
- **RESTful API design** following industry best practices
- **Input validation** with Pydantic models for data integrity
- **SQLModel integration** for elegant database modeling
- **Advanced filtering and sorting** capabilities
- **Comprehensive test suite** with pytest for reliability
- **Modern Python tooling** with uv for fast dependency management
- **Interactive API documentation** with automatic OpenAPI/Swagger generation
- **Database migration support** with SQLModel
- **Environment-based configuration** for flexible deployment

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Project Structure](#project-structure)
- [Commands](#commands)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.8 or higher
- `uv` package manager (install with `pip install uv`)
- PostgreSQL database (for production) or SQLite (for development)
- Git version control system

## Installation and Setup

### Quick Start

```bash
# Clone the repository (if applicable)
git clone <repository-url>
cd task_management_api

# Install dependencies with uv
uv sync

# Activate the virtual environment (optional but recommended)
source .venv/bin/activate
```

### Manual Installation

```bash
# Install uv if you don't have it
pip install uv

# Navigate to the project directory
cd task_management_api

# Install dependencies
uv sync

# Verify installation by running tests
uv run pytest tests/
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Database Configuration
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=your_host
POSTGRES_DB=your_database
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}/${POSTGRES_DB}

# For local development with SQLite
USE_SQLITE_FALLBACK=true
SQLITE_DB_PATH=./task_management.db

# Optional configurations
DEBUG=true
LOG_LEVEL=info
MAX_TASKS_PER_USER=100
```

### Database Options

The application supports both PostgreSQL and SQLite databases:

#### PostgreSQL (Production)
- Default database for production environments
- Supports concurrent access and advanced features
- Configure with PostgreSQL connection details

#### SQLite (Development)
- Fallback option for local development
- No setup required, file-based database
- Enable with `USE_SQLITE_FALLBACK=true`

## Running the Application

### Development Mode

```bash
# Method 1: Using uv directly
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Makefile
make run

# Method 3: Using Python module
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Run without auto-reload for production
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Server Information

- **Base URL**: `http://localhost:8000`
- **API Base**: `http://localhost:8000/api/v1`
- **Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

## API Documentation

The API comes with comprehensive, automatically-generated documentation:

- **Swagger UI**: Accessible at `http://localhost:8000/docs`
- **ReDoc**: Available at `http://localhost:8000/redoc`
- **OpenAPI JSON**: Available at `http://localhost:8000/openapi.json`

The interactive documentation allows you to test endpoints directly from your browser.

## API Endpoints

### Base URL
`http://localhost:8000/api/v1`

### 1. Create a Task
- **Method**: `POST`
- **Endpoint**: `/tasks/`
- **Description**: Create a new task with specified properties
- **Authentication**: Optional (depends on configuration)
- **Request Body**:
```json
{
  "title": "string (required, 1-100 characters)",
  "description": "string (optional, max 500 characters)",
  "is_completed": "boolean (default: false)",
  "priority": "string (default: medium, options: low, medium, high, urgent)"
}
```
- **Response**: `201 Created`
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "is_completed": "boolean",
  "priority": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "description": "Finish the task management API",
    "is_completed": false,
    "priority": "high"
  }'
```

### 2. Get a Task
- **Method**: `GET`
- **Endpoint**: `/tasks/{task_id}`
- **Description**: Retrieve a specific task by its unique ID
- **Path Parameter**: `task_id` (integer)
- **Response**: `200 OK`
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "is_completed": "boolean",
  "priority": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/1"
```

### 3. List All Tasks
- **Method**: `GET`
- **Endpoint**: `/tasks/`
- **Description**: Retrieve all tasks with pagination, filtering, and sorting options
- **Query Parameters**:
  - `skip` (integer, default: 0) - Number of records to skip
  - `limit` (integer, default: 100) - Maximum number of records to return
  - `is_completed` (boolean, optional) - Filter by completion status
  - `priority` (string, optional) - Filter by priority level (low, medium, high, urgent)
  - `sort_by` (string, default: created_at) - Field to sort by (title, created_at, updated_at, is_completed, priority)
  - `sort_order` (string, default: desc) - Sort order (asc, desc)
- **Response**: `200 OK`
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
- **Example Requests**:
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

# Paginated results (first 10 tasks)
curl -X GET "http://localhost:8000/api/v1/tasks/?skip=0&limit=10"
```

### 4. Update a Task
- **Method**: `PUT`
- **Endpoint**: `/tasks/{task_id}`
- **Description**: Update an existing task with new information
- **Path Parameter**: `task_id` (integer)
- **Request Body** (all fields optional):
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "is_completed": "boolean (optional)",
  "priority": "string (optional, options: low, medium, high, urgent)"
}
```
- **Response**: `200 OK`
```json
{
  "id": "integer",
  "title": "string",
  "description": "string",
  "is_completed": "boolean",
  "priority": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```
- **Example Request**:
```bash
curl -X PUT "http://localhost:8000/api/v1/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated task title",
    "is_completed": true,
    "priority": "medium"
  }'
```

### 5. Delete a Task
- **Method**: `DELETE`
- **Endpoint**: `/tasks/{task_id}`
- **Description**: Permanently remove a task by its ID
- **Path Parameter**: `task_id` (integer)
- **Response**: `200 OK`
```json
{
  "message": "Task deleted successfully"
}
```
- **Example Request**:
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/1"
```

## Error Responses

The API returns appropriate HTTP status codes and error messages:

| Status Code | Description | Example |
|-------------|-------------|---------|
| `200 OK` | Successful request | Standard response for successful GET, PUT, DELETE requests |
| `201 Created` | Resource successfully created | Response for successful POST requests |
| `400 Bad Request` | Invalid request format | Malformed JSON or invalid parameters |
| `404 Not Found` | Resource does not exist | Requested task ID does not exist |
| `422 Unprocessable Entity` | Validation error | Invalid request parameters or data |
| `500 Internal Server Error` | Server error | Unexpected server-side issues |

### Error Response Format
```json
{
  "detail": "Error message describing the issue"
}
```

## Testing

The application includes a comprehensive test suite to ensure reliability:

```bash
# Run all tests
uv run pytest tests/

# Run tests with verbose output
uv run pytest tests/ -v

# Run tests with coverage report
uv run pytest tests/ --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_tasks.py

# Run tests and show coverage percentage
uv run pytest tests/ --cov=app --cov-report=term-missing
```

### Test Structure

Tests are organized in the `tests/` directory:
- `conftest.py` - Shared fixtures and test configuration
- `test_tasks.py` - Tests for task CRUD operations
- `test_main.py` - Tests for main application endpoints

## Project Structure

```
task_management_api/
├── app/
│   ├── main.py             # Main application entry point
│   ├── database.py         # Database configuration and session management
│   ├── models/
│   │   └── task.py        # Task model definitions with SQLModel
│   ├── crud/
│   │   └── task.py        # CRUD operations for tasks
│   ├── routes/
│   │   └── tasks.py       # API route handlers
│   └── config.py          # Application configuration settings
├── tests/
│   ├── conftest.py        # Test fixtures and configuration
│   ├── test_tasks.py      # Task-related API tests
│   └── test_main.py       # Main app functionality tests
├── scripts/
│   └── init_db.py         # Database initialization script
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore patterns
├── pyproject.toml         # Project dependencies and metadata
├── uv.lock               # Dependency lock file
├── Makefile              # Convenient development commands
├── README.md             # Project documentation
└── task_management.db    # SQLite database file (if using SQLite)
```

## Commands

The project includes a Makefile with convenient commands:

```bash
# Install dependencies
make install

# Run the application in development mode
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

# Check code quality
make check

# Install and run everything
make all
```

## Deployment

### Local Deployment

For local development and testing:

1. Follow the installation steps above
2. Set up environment variables
3. Run the application with `make run`

### Containerized Deployment (Docker)

Coming soon - Docker configuration for containerized deployment.

### Production Deployment

For production deployment:

1. Use PostgreSQL instead of SQLite
2. Set appropriate environment variables
3. Use a WSGI server like Gunicorn
4. Set up a reverse proxy (nginx, Apache)
5. Implement proper logging and monitoring

Example production command:
```bash
gunicorn app.main:app --workers 4 --bind 0.0.0.0:8000 --timeout 120
```

## Contributing

We welcome contributions to this project! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`make test`)
6. Format your code (`make format`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Development Guidelines

- Follow PEP 8 coding standards
- Write comprehensive tests for new features
- Document public APIs with docstrings
- Keep functions focused and small
- Use type hints for better code clarity

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the API documentation at `http://localhost:8000/docs`
2. Review the error logs for detailed information
3. Create an issue in the repository with detailed information
4. Contact the development team

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Database management with [SQLModel](https://sqlmodel.tiangolo.com/)
- Package management with [uv](https://github.com/astral-sh/uv)
- Testing with [pytest](https://docs.pytest.org/)