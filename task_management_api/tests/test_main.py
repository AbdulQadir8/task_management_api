from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import engine
from sqlalchemy.pool import StaticPool

# Create an in-memory database for testing
test_engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)

def get_test_session():
    SQLModel.metadata.create_all(test_engine)
    with Session(test_engine) as session:
        yield session

# Override the dependency
from app.routes import tasks
from app.database import get_session

def override_get_session():
    yield next(get_test_session())

app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Task Management API"}